
(function () {
    const script = document.currentScript;
    const WIDGET_ID = script.dataset.widgetId;

    window['getWidgetContent_' + WIDGET_ID] = function () {
        return {
            id: WIDGET_ID,
            html: `
                <h2>Live Traffic Log</h2>
                <pre id="traffic-log-list">Monitoring...</pre>
            `,
            settings: {},
            init: function () { },
            destroy: function () { }
        };
    };
})();
