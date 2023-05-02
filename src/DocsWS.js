export default class DocsWebSocket extends WebSocket {

    constructor(url, protocols) {
        super(url, protocols);

        this.onmessage_before_handler = null;
        this.onmessage_handler = null;
        this.onmessage_after_handler = null;

        this.onopen = null;
        this.onmessage = (ev) => {
            if (this.onmessage_before_handler) this.onmessage_before_handler(ev);
            if (this.onmessage_handler) this.onmessage_handler(ev);
            if (this.onmessage_after_handler) this.onmessage_after_handler(ev);
        };
        this.onclose = null;
        this.onerror = null;
    }
}