(function() {
    "use strict";
    function initTPV() {
        if (typeof $ === 'undefined') {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() { setTimeout(initTPV, 100); });
            } else {
                setTimeout(initTPV, 100);
            }
            return;
        }
        var TPV = window.TPV = {
    currentTableId: null,
    currentOrderId: null,
    currentCategoryId: 0,
    data: null,

    init: function() {
        var self = this;
        $.getJSON('/web/session/get_session_info', function(session) {
            $('#tpv-waiter').text(session.username);
        });
        this.loadData();
        // Payment method selector
        $(document).on('click', '.tpv-pay-method', function() {
            $('.tpv-pay-method').removeClass('active');
            $(this).addClass('active');
            $(this).find('input[type="radio"]').prop('checked', true);
            var method = $(this).data('method');
            if (method === 'cash') {
                $('#pay-cash-section').show();
                self.calcChange();
            } else {
                $('#pay-cash-section').hide();
            }
        });
        // Change calculation on amount input
        $(document).on('input', '#pay-amount', function() {
            self.calcChange();
        });
    },
    
    calcChange: function() {
        var order = this.data.orders.find(function(o) { return o.id === this.currentOrderId; }.bind(this));
        if (!order) return;
        var total = order.amount_total;
        var received = parseFloat($('#pay-amount').val()) || 0;
        if (received >= total) {
            $('#pay-change').text((received - total).toFixed(2) + '€');
            $('#pay-change-row').show();
        } else {
            $('#pay-change-row').hide();
        }
    },

    loadData: function() {
        var self = this;
        this.rpc('/restaurant/tpv/data', {}).then(function(data) {
            self.data = data;
            self.renderAreas();
            self.renderTables();
            self.renderCategories();
            self.renderItems();
            if (self.currentOrderId) {
                self.refreshCart();
            }
        });
    },

    rpc: function(url, params) {
        return $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({params: params}),
            dataType: 'json',
        }).then(function(res) { return res.result; });
    },

    renderAreas: function() {
        var self = this;
        var container = $('.tpv-area-filter');
        container.empty();
        container.append('<button class="active" data-area="0">Todas</button>');
        this.data.areas.forEach(function(a) {
            container.append('<button data-area="' + a.id + '">' + a.name + '</button>');
        });
        container.find('button').click(function() {
            container.find('button').removeClass('active');
            $(this).addClass('active');
            self.renderTables();
        });
    },

    renderTables: function() {
        var self = this;
        var areaId = parseInt($('.tpv-area-filter .active').data('area'));
        var container = $('#tpv-tables');
        container.empty();
        var filtered = areaId ? this.data.tables.filter(function(t) { return t.area_id === areaId; }) : this.data.tables;
        filtered.forEach(function(t) {
            var order = null;
            if (t.current_order_id) {
                order = self.data.orders.find(function(o) { return o.id === t.current_order_id; });
            }
            var card = $('<div class="tpv-table-card ' + t.status + '">' +
                '<div class="table-name">' + t.name + '</div>' +
                '<div class="table-status">' + t.status + '</div>' +
                (order ? '<div class="table-order">' + order.amount_total.toFixed(2) + '\u20AC</div>' : '') +
                '<div class="table-capacity"><i class="fas fa-user"></i> ' + t.capacity + '</div>' +
            '</div>');
            card.click(function() { self.selectTable(t.id); });
            container.append(card);
        });
    },

    selectTable: function(tableId) {
        var self = this;
        this.currentTableId = tableId;
        var table = this.data.tables.find(function(t) { return t.id === tableId; });
        if (!table) return;

        if (table.current_order_id) {
            this.currentOrderId = table.current_order_id;
            this.openOrderPanel();
        } else {
            this.rpc('/restaurant/tpv/create_order', {table_id: tableId}).then(function(res) {
                if (res.error) { alert(res.error); return; }
                self.currentOrderId = res.order_id;
                self.openOrderPanel();
                self.loadData();
            });
        }
    },

    openOrderPanel: function() {
        var self = this;
        var table = this.data.tables.find(function(t) { return t.id === self.currentTableId; });
        var order = this.data.orders.find(function(o) { return o.id === self.currentOrderId; });

        $('#tpv-table-select').hide();
        $('#tpv-order-panel').show();
        $('#tpv-kitchen-status').empty();
        if (order) {
            $('#tpv-order-table').text('Mesa ' + table.name + ' - ' + order.name);
            var allPending = order.lines.every(function(l) { return l.state === 'pending'; });
            var allCooked = order.lines.every(function(l) { return l.state === 'cooking'; });
            var allServed = order.lines.every(function(l) { return l.state === 'served'; });
            if (allServed) {
                $('#tpv-kitchen-status').html('<span class="badge badge-success">Todo servido</span>');
            } else if (allCooked && !allServed) {
                $('#tpv-kitchen-status').html('<span class="badge badge-info">Listo para servir</span>');
            } else if (!allPending) {
                $('#tpv-kitchen-status').html('<span class="badge badge-warning">En cocina</span>');
            }
        } else {
            $('#tpv-order-table').text('Mesa ' + table.name);
        }
        $('#tpv-order-waiter').text('Mesero: ' + $('#tpv-waiter').text());
        this.refreshCart();
    },

    renderCategories: function() {
        var self = this;
        var container = $('#tpv-categories');
        container.empty();
        container.append('<button class="active" data-id="0">Todas</button>');
        this.data.categories.forEach(function(c) {
            container.append('<button data-id="' + c.id + '">' + c.name + '</button>');
        });
        container.find('button').click(function() {
            container.find('button').removeClass('active');
            $(this).addClass('active');
            self.currentCategoryId = parseInt($(this).data('id'));
            self.renderItems();
        });
    },

    renderItems: function() {
        var self = this;
        var container = $('#tpv-items');
        container.empty();
        var filtered = this.currentCategoryId ?
            this.data.items.filter(function(i) { return i.category_id === self.currentCategoryId; }) :
            this.data.items;
        filtered.forEach(function(item) {
            var btn = $('<div class="tpv-item-btn">' +
                '<span class="item-name">' + item.name + '</span>' +
                '<span class="item-price">' + item.price.toFixed(2) + '\u20AC</span>' +
            '</div>');
            btn.click(function() { self.addItem(item.id); });
            container.append(btn);
        });
    },

    addItem: function(itemId) {
        var self = this;
        this.rpc('/restaurant/tpv/add_line', {order_id: this.currentOrderId, item_id: itemId}).then(function(res) {
            self.updateFromResponse(res);
            self.loadData();
        });
    },

    updateLine: function(lineId, qty) {
        var self = this;
        this.rpc('/restaurant/tpv/update_line', {line_id: lineId, quantity: qty}).then(function(res) {
            self.updateFromResponse(res);
        });
    },

    refreshCart: function() {
        var self = this;
        var order = this.data.orders.find(function(o) { return o.id === self.currentOrderId; });
        if (order) {
            self.updateFromResponse({lines: order.lines, amount_total: order.amount_total});
        }
    },

    updateFromResponse: function(res) {
        var container = $('#tpv-cart-lines');
        container.empty();
        res.lines.forEach(function(l) {
            var stateIcon = '';
            if (l.state === 'cooking') stateIcon = ' <i class="fas fa-fire" style="color:#e67e22"></i>';
            else if (l.state === 'served') stateIcon = ' <i class="fas fa-check-circle" style="color:#27ae60"></i>';
            var line = $('<div class="tpv-cart-line">' +
                '<span class="line-name">' + l.name + stateIcon + '</span>' +
                '<span class="line-qty"><input type="number" value="' + l.quantity + '" min="0" step="1"/></span>' +
                '<span class="line-subtotal">' + l.price_subtotal.toFixed(2) + '\u20AC</span>' +
                (l.state === 'pending' ? '<span class="line-remove"><i class="fas fa-times"></i></span>' : '') +
            '</div>');
            if (l.state === 'pending') {
                line.find('.line-qty input').change(function() {
                    TPV.updateLine(l.id, parseInt($(this).val()) || 0);
                });
                line.find('.line-remove').click(function() {
                    TPV.updateLine(l.id, 0);
                });
            } else {
                line.find('.line-qty input').prop('disabled', true);
            }
            container.append(line);
        });
        if (res.amount_total !== undefined) {
            $('#tpv-order-amount').text(res.amount_total.toFixed(2) + '\u20AC');
            $('#tpv-cart-total').text(res.amount_total.toFixed(2) + '\u20AC');
        }
    },

    sendToKitchen: function() {
        var self = this;
        this.rpc('/restaurant/tpv/send_kitchen', {order_id: this.currentOrderId}).then(function(res) {
            if (res.state) {
                $('#tpv-kitchen-status').html('<span class="badge badge-warning">En cocina</span>');
            }
            self.loadData();
        });
    },

    serveOrder: function() {
        var self = this;
        this.rpc('/restaurant/tpv/serve', {order_id: this.currentOrderId}).then(function(res) {
            if (res.state) {
                $('#tpv-kitchen-status').html('<span class="badge badge-info">Listo para servir</span>');
            }
            self.loadData();
        });
    },

    showPayment: function() {
        var order = this.data.orders.find(function(o) { return o.id === this.currentOrderId; }.bind(this));
        var total = order ? order.amount_total : 0;
        $('#pay-total').text(total.toFixed(2) + '\u20AC');
        $('#pay-amount').val(total.toFixed(2));
        $('#tpv-payment-modal').show();
    },

    closePayment: function() {
        $('#tpv-payment-modal').hide();
    },

    confirmPayment: function() {
        var self = this;
        var amount = parseFloat($('#pay-amount').val()) || 0;
        var method = $('input[name="method"]:checked').val();
        this.rpc('/restaurant/tpv/pay', {order_id: this.currentOrderId, amount: amount, method: method}).then(function(res) {
            self.closePayment();
            $('#tpv-order-panel').hide();
            $('#tpv-table-select').show();
            self.currentOrderId = null;
            self.currentTableId = null;
            self.loadData();
        });
    }
};
        TPV.init();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTPV);
    } else {
        initTPV();
    }
})();