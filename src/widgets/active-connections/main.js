
(function () {
    const script = document.currentScript;
    const WIDGET_ID = script.dataset.widgetId;

    window['getWidgetContent_' + WIDGET_ID] = function () {
        return {
            id: WIDGET_ID,
            html: `
                <h2>Active Connections <span id="active-count" class="widget-count"></span></h2>
                <pre id="active-list">Loading...</pre>
            `,
            settings: {},
            init: function () { },
            destroy: function () { }
        };
    };
})();
