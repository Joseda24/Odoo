/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";

const COLORS = [
    ["#7c7bad", "#6c63a0"],
    ["#e8794b", "#d4683e"],
    ["#4f9cf7", "#3b82e0"],
    ["#34d399", "#22b87a"],
    ["#f472b6", "#e05a9e"],
    ["#60a5fa", "#4287e0"],
    ["#a78bfa", "#8b6fe0"],
    ["#fbbf24", "#e8a800"],
    ["#6ee7b7", "#4ad699"],
    ["#f87171", "#e05555"],
    ["#38bdf8", "#1ea0e0"],
    ["#c084fc", "#a866e0"],
    ["#fb923c", "#e07a2a"],
    ["#4ade80", "#2ec460"],
    ["#e8794b", "#d4683e"],
];

function escapeHTML(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
}

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this._drawerEl = null;
        this._keyHandler = null;
        this._searchTerm = "";
        this._focusedIndex = -1;
        this.userId = false;
        onMounted(() => this._initDrawer());
        onPatched(() => this._initDrawer());
        onWillUnmount(() => this._destroyDrawer());
    },

    _initDrawer() {
        if (!this.root || !this.root.el) return;
        if (this.root.el.querySelector("[data-custom-apps-btn]")) return;
        const nav = this.root.el.querySelector("nav.o_main_navbar");
        if (!nav) return;
        const orig = this.root.el.querySelector(".o_navbar_apps_menu");
        if (orig) orig.style.display = "none";
        const btn = document.createElement("button");
        btn.dataset.customAppsBtn = "1";
        btn.className = "btn border-0 px-3 d-flex align-items-center h-100 o_navbar_apps_menu_toggle";
        btn.title = "Aplicaciones";
        btn.innerHTML = '<i class="oi oi-apps"></i>';
        btn.addEventListener("click", (ev) => { ev.preventDefault(); this._toggleDrawer(); });
        const brand = nav.querySelector(".o_menu_brand");
        brand ? nav.insertBefore(btn, brand) : nav.insertBefore(btn, nav.firstChild);
    },

    async _toggleDrawer() { this._drawerEl ? this._destroyDrawer() : await this._openDrawer(); },

    async _openDrawer() {
        this._destroyDrawer();
        this._searchTerm = "";
        this._focusedIndex = -1;
        const container = document.createElement("div");
        container.id = "o_custom_app_drawer";
        this._drawerEl = container;
        // fetch chat/activity data before rendering so badge is correct
        await this._fetchInitialData();
        this._renderDrawer(container);
        document.body.appendChild(container);
    },

    async _fetchInitialData() {
        try {
            const [members] = await Promise.all([
                this._rpc("discuss.channel.member", "search_read", [], {
                    domain: [["is_self", "=", true]],
                    fields: ["message_unread_counter", "channel_id"],
                    limit: 100
                }).catch(() => [])
            ]);
            this._chatMembers = members || [];
        } catch (_) {
            this._chatMembers = [];
        }
        try {
            const uidEl = document.querySelector("[data-uid]");
            if (uidEl && uidEl.dataset.uid) this.userId = parseInt(uidEl.dataset.uid, 10);
        } catch (_) {}
    },

    _renderDrawer(container) {
        const apps = this.menuService.getApps();
        let userName = "Usuario";
        let avatarSrc = "";
        try {
            const nameEl = document.querySelector(".o_user_menu .o_user_name, .o_menu_user_name");
            if (nameEl) userName = nameEl.textContent.trim();
            const imgEl = document.querySelector(".o_user_menu img, .o_menu_user_avatar");
            if (imgEl && imgEl.src) avatarSrc = imgEl.src;
        } catch (_) {}

        container.innerHTML = `
        <div class="o_app_drawer_backdrop"></div>
        <div class="o_app_drawer">
          <div class="o_app_drawer_topbar">
            <div class="o_app_drawer_topbar_actions">
              <button type="button" class="o_topbar_action" data-action="chat" title="Chat">
                <i class="fa fa-comment"></i>
                <span class="o_badge"></span>
              </button>
              <button type="button" class="o_topbar_action" data-action="activities" title="Actividades">
                <i class="fa fa-clock-o"></i>
              </button>
              <button type="button" class="o_topbar_action o_topbar_action_user" data-action="user" title="${escapeHTML(userName)}">
                ${avatarSrc ? `<img src="${escapeHTML(avatarSrc)}" alt=""/>` : `<span class="o_user_initials">${(userName.charAt(0) || "?").toUpperCase()}</span>`}
                <span class="o_user_name">${escapeHTML(userName)}</span>
              </button>
            </div>
          </div>
          <div class="o_app_drawer_inner">
            <div class="o_app_drawer_search">
              <button type="button" class="o_app_drawer_toggle_close" aria-label="Cerrar">
                <i class="oi oi-apps"></i>
              </button>
              <i class="oi oi-search"></i>
              <input type="text" class="o_app_drawer_search_input"
                     placeholder="Buscar aplicación..." autofocus/>
              <button type="button" class="o_search_clear" style="display:none"><i class="oi oi-x"></i></button>
            </div>
            <div class="o_app_drawer_body">
              ${this._buildGrid(apps, "")}
            </div>
          </div>
        </div>`;
        container.querySelector(".o_app_drawer_backdrop").addEventListener("click", () => this._destroyDrawer());
        const toggleClose = container.querySelector(".o_app_drawer_toggle_close");
        if (toggleClose) toggleClose.addEventListener("click", () => this._destroyDrawer());
        this._setupTopbar(container);
        const input = container.querySelector(".o_app_drawer_search_input");
        const clearBtn = container.querySelector(".o_search_clear");
        const body = container.querySelector(".o_app_drawer_body");
        if (input) {
            input.addEventListener("input", (ev) => {
                this._searchTerm = ev.target.value;
                this._focusedIndex = -1;
                if (body) {
                    body.scrollTop = 0;
                    body.innerHTML = this._buildGrid(this.menuService.getApps(), ev.target.value);
                    this._addClickHandlers(body);
                }
                clearBtn.style.display = ev.target.value ? "flex" : "none";
            });
            input.addEventListener("keydown", (ev) => this._onKeyDown(ev, body));
            setTimeout(() => input.focus(), 50);
        }
        if (clearBtn) {
            clearBtn.addEventListener("click", () => {
                if (input) {
                    input.value = "";
                    this._searchTerm = "";
                    this._focusedIndex = -1;
                    if (body) {
                        body.scrollTop = 0;
                        body.innerHTML = this._buildGrid(this.menuService.getApps(), "");
                        this._addClickHandlers(body);
                    }
                    clearBtn.style.display = "none";
                    input.focus();
                }
            });
        }
        this._addClickHandlers(body);
        this._keyHandler = (ev) => { if (ev.key === "Escape") this._destroyDrawer(); };
        document.addEventListener("keydown", this._keyHandler);
    },

    _onKeyDown(ev, body) {
        if (!body) return;
        const items = body.querySelectorAll(".o_app_drawer_item");
        if (!items.length) return;
        const step = ev.shiftKey ? 5 : 1;
        if (ev.key === "ArrowDown") { ev.preventDefault(); this._focusedIndex = Math.min(this._focusedIndex + step, items.length - 1); this._focusItem(items); }
        else if (ev.key === "ArrowUp") { ev.preventDefault(); this._focusedIndex = Math.max(this._focusedIndex - step, 0); this._focusItem(items); }
        else if (ev.key === "Home") { ev.preventDefault(); this._focusedIndex = 0; this._focusItem(items); }
        else if (ev.key === "End") { ev.preventDefault(); this._focusedIndex = items.length - 1; this._focusItem(items); }
        else if (ev.key === "PageUp") { ev.preventDefault(); this._focusedIndex = Math.max(this._focusedIndex - 12, 0); this._focusItem(items); }
        else if (ev.key === "PageDown") { ev.preventDefault(); this._focusedIndex = Math.min(this._focusedIndex + 12, items.length - 1); this._focusItem(items); }
        else if (ev.key === "Enter" && this._focusedIndex >= 0 && items[this._focusedIndex]) { ev.preventDefault(); items[this._focusedIndex].click(); }
    },

    _focusItem(items) {
        items.forEach((el, i) => el.classList.toggle("o_app_drawer_item_focused", i === this._focusedIndex));
        if (items[this._focusedIndex]) items[this._focusedIndex].scrollIntoView({ block: "nearest", behavior: "smooth" });
    },

    _buildGrid(apps, filter) {
        const term = (filter || "").toLowerCase().trim();
        let filtered = term ? apps.filter(a => (a.name || "").toLowerCase().includes(term)) : apps;
        const count = filtered.length;
        if (count === 0) {
            return `<div class="o_app_drawer_empty">
              <i class="oi oi-search"></i>
              <span>No se encontraron aplicaciones para "${escapeHTML(filter)}"</span>
            </div>`;
        }
        let html = "";
        if (term) {
            html += `<div class="o_app_drawer_result_count">${count} ${count === 1 ? "resultado" : "resultados"}</div>`;
        }
        html += `<div class="o_app_drawer_grid">${this._buildCards(filtered, term)}</div>`;
        return html;
    },

    _buildCards(apps, term) {
        return apps.map((app, i) => {
            const c = i % COLORS.length;
            const rawName = app.name || "";
            const name = escapeHTML(rawName);
            const displayName = term ? name.replace(new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"), "<mark>$1</mark>") : name;
            const icon = app.webIconData;
            const iconHtml = icon ? `<img src="${escapeHTML(icon)}" alt="${name}" loading="lazy"/>` : `<span class="o_app_initials">${rawName.charAt(0).toUpperCase() || "?"}</span>`;
            return `<a role="menuitem" class="o_app_drawer_item"
               href="${escapeHTML(this.getMenuItemHref(app))}"
               data-app-id="${escapeHTML(app.id)}"
               title="${name}"
               style="--i: ${i}; --bg: ${COLORS[c][0]}; --bg2: ${COLORS[c][1]}">
              <div class="o_app_icon_wrap">
                ${iconHtml}
              </div>
              <span class="o_app_name">${displayName}</span>
            </a>`;
        }).join("");
    },

    _addClickHandlers(parent) {
        if (!parent) return;
        parent.querySelectorAll(".o_app_drawer_item").forEach(el => {
            el.addEventListener("click", () => this._destroyDrawer());
        });
    },

    _setupTopbar(container) {
        this._closeTopbarDropdown(container);
        this._updateChatBadge(container);
        // get current user id
        try {
            const menuData = document.querySelector(".o_user_menu");
            if (menuData && menuData.dataset.uid) {
                this.userId = parseInt(menuData.dataset.uid, 10);
            }
        } catch (_) {}
        container.querySelectorAll(".o_topbar_action").forEach(btn => {
            btn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                const action = btn.dataset.action;
                if (action === "user") { this._toggleUserDropdown(container, btn); return; }
                if (action === "chat") { this._toggleChatDropdown(container, btn); return; }
                if (action === "activities") { this._toggleActivitiesDropdown(container, btn); return; }
                this._destroyDrawer();
            });
        });
        document.addEventListener("click", (ev) => {
            if (container.contains(document.activeElement)) return;
            this._closeTopbarDropdown(container);
        }, { once: false });
    },

    _updateChatBadge(container) {
        const members = this._chatMembers || [];
        const details = members.map(m => `${m.channel_id?.[1] || "?"}:${m.message_unread_counter || 0}`).join(", ");
        const total = members.reduce((sum, m) => sum + (m.message_unread_counter || 0), 0);
        const withUnread = members.filter(m => (m.message_unread_counter || 0) > 0);
        const badge = container.querySelector(".o_badge");
        if (badge) {
            badge.textContent = total > 0 ? (total > 99 ? "99+" : total) : "";
            badge.style.display = total > 0 ? "flex" : "none";
            badge.title = `Total sin leer: ${total} | Canales con no leídos: ${withUnread.length} | ${details}`;
        }
    },

    _toggleChatDropdown(container, btn) {
        const existing = container.querySelector(".o_app_drawer_user_dropdown");
        if (existing) { existing.remove(); return; }
        this._closeTopbarDropdown(container);
        const members = this._chatMembers || [];
        this._renderChatDropdown(btn, members);
    },

    async _renderChatDropdown(btn, members) {
        const dd = document.createElement("div");
        dd.className = "o_app_drawer_user_dropdown";
        dd.style.width = "300px";
        dd.innerHTML = `<div class="o_dropdown_item" style="justify-content:center;cursor:default"><i class="fa fa-spinner fa-spin"></i> Cargando...</div>`;
        btn.appendChild(dd);
        if (!members.length) {
            dd.innerHTML = `<div class="o_dropdown_item" style="justify-content:center;cursor:default;flex-direction:column;gap:4px;padding:16px 12px">
              <span style="opacity:0.3;font-size:1.2rem">💬</span>
              <span style="opacity:0.5;font-size:0.75rem">No hay conversaciones</span>
            </div>`;
            return;
        }
        // Fetch channel details (name, channel_type) for all unique channels
        const channelIds = [...new Set(members.map(m => m.channel_id?.[0]).filter(Boolean))];
        let channels = [];
        try {
            channels = await this._rpc("discuss.channel", "search_read", [], {
                domain: [["id", "in", channelIds]],
                fields: ["name", "channel_type"],
                limit: 100
            }) || [];
        } catch (_) {}
        const channelMap = {};
        for (const c of channels) channelMap[c.id] = c;
        const enriched = members.map(m => {
            const ch = channelMap[m.channel_id?.[0]] || {};
            return {
                name: ch.name || m.channel_id?.[1] || "Sin nombre",
                channel_type: ch.channel_type || "chat",
                message_unread_counter: m.message_unread_counter || 0,
            };
        });
        const chats = enriched.filter(c => c.channel_type === "chat");
        const canales = enriched.filter(c => c.channel_type !== "chat");
        dd.innerHTML = `
          <div class="o_dropdown_tabs">
            <button type="button" class="o_dropdown_tab active" data-tab="all">Todos (${enriched.length})</button>
            <button type="button" class="o_dropdown_tab" data-tab="chats">Chats (${chats.length})</button>
            <button type="button" class="o_dropdown_tab" data-tab="canales">Canales (${canales.length})</button>
          </div>
          <div class="o_dropdown_tab_content">
            ${enriched.map(c => this._channelHTML(c)).join("")}
          </div>`;
        const content = dd.querySelector(".o_dropdown_tab_content");
        dd.querySelectorAll(".o_dropdown_tab").forEach(tab => {
            tab.addEventListener("click", (ev) => {
                ev.stopPropagation();
                dd.querySelectorAll(".o_dropdown_tab").forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                const t = tab.dataset.tab;
                const list = t === "all" ? enriched : t === "chats" ? chats : canales;
                content.innerHTML = list.map(c => this._channelHTML(c)).join("");
            });
        });
    },

    _channelHTML(c) {
        const name = escapeHTML(c.name || "Sin nombre");
        const unread = c.message_unread_counter || 0;
        const badge = unread ? `<span class="o_channel_badge">${unread > 99 ? "99+" : unread}</span>` : "";
        return `<div class="o_dropdown_item" style="cursor:default">
          <span style="font-size:0.8rem;color:rgba(255,255,255,0.7)">${name}</span>
          ${badge}
        </div>`;
    },

    async _toggleActivitiesDropdown(container, btn) {
        const existing = container.querySelector(".o_app_drawer_user_dropdown");
        if (existing) { existing.remove(); return; }
        this._closeTopbarDropdown(container);
        const dd = document.createElement("div");
        dd.className = "o_app_drawer_user_dropdown";
        dd.style.width = "280px";
        dd.innerHTML = `<div class="o_dropdown_item" style="justify-content:center;cursor:default"><i class="fa fa-spinner fa-spin"></i> Cargando...</div>`;
        btn.appendChild(dd);
        try {
            const domain = this.userId ? [["user_id", "=", this.userId]] : [];
            const data = await this._rpc("mail.activity", "search_read", [], {
                domain: domain,
                fields: ["summary", "date_deadline", "activity_type_id", "res_name", "res_model"],
                limit: 10, order: "date_deadline ASC"
            });
            if (!data || !data.length) throw new Error("empty");
            let items = "";
            for (const a of data) {
                const summary = a.summary || a.res_name || "Sin descripción";
                const deadline = a.date_deadline || "";
                const typeName = a.activity_type_id?.[1] || "";
                items += `<div class="o_dropdown_item" style="flex-direction:column;align-items:stretch;gap:2px;cursor:default">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.7)">${escapeHTML(summary.slice(0, 50))}</span>
                    <span style="font-size:0.6rem;color:rgba(255,255,255,0.3)">${escapeHTML(deadline)}</span>
                  </div>
                  <span style="font-size:0.65rem;color:rgba(255,255,255,0.35)">${escapeHTML(typeName)}</span>
                </div>`;
            }
            dd.innerHTML = items;
        } catch (_) {
            dd.innerHTML = `<div class="o_dropdown_item" style="justify-content:center;cursor:default;flex-direction:column;gap:4px;padding:16px 12px">
              <span style="opacity:0.3;font-size:1.2rem">📋</span>
              <span style="opacity:0.5;font-size:0.75rem">No hay actividades recientes</span>
            </div>`;
        }
    },

    async _rpc(model, method, args, kwargs) {
        const res = await fetch("/web/dataset/call_kw", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0", method: "call",
                params: { model, method, args, kwargs },
                id: Math.random().toString(16).slice(2)
            })
        });
        if (!res.ok) throw new Error(res.status + " " + res.statusText);
        const json = await res.json();
        if (json.error) throw new Error(json.error.data?.message || json.error.message);
        return json.result;
    },

    _toggleUserDropdown(container, btn) {
        const existing = container.querySelector(".o_app_drawer_user_dropdown");
        if (existing) { existing.remove(); return; }
        this._closeTopbarDropdown(container);
        const dd = document.createElement("div");
        dd.className = "o_app_drawer_user_dropdown";
        dd.innerHTML = `
          <button type="button" class="o_dropdown_item" data-action="preferences">
            <i class="fa fa-user"></i> Preferencias
          </button>
          <div class="o_dropdown_divider"></div>
          <button type="button" class="o_dropdown_item" data-action="account">
            <i class="fa fa-cog"></i> Mi cuenta
          </button>
          <div class="o_dropdown_divider"></div>
          <button type="button" class="o_dropdown_item o_dropdown_danger" data-action="logout">
            <i class="fa fa-sign-out"></i> Cerrar sesión
          </button>`;
        btn.appendChild(dd);
        dd.querySelectorAll(".o_dropdown_item").forEach(item => {
            item.addEventListener("click", (ev) => {
                ev.stopPropagation();
                const a = item.dataset.action;
                this._closeTopbarDropdown(container);
                this._destroyDrawer();
                if (a === "logout") window.location.href = "/web/session/logout";
                else if (a === "preferences") window.location.href = "/web?action=base.action_preferences";
                else if (a === "account") window.location.href = "/web?action=base.action_preferences";
            });
        });
    },

    _closeTopbarDropdown(container) {
        const dd = container.querySelector(".o_app_drawer_user_dropdown");
        if (dd) dd.remove();
    },

    _destroyDrawer() {
        if (this._keyHandler) { document.removeEventListener("keydown", this._keyHandler); this._keyHandler = null; }
        if (this._drawerEl) {
            const el = this._drawerEl;
            this._drawerEl = null;
            el.classList.add("o_drawer_closing");
            setTimeout(() => el.remove(), 200);
        }
    },
});
