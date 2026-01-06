import network
from lib import tinyweb

def start_server(wlan: network.WLAN):
    ip = wlan.ifconfig()[0]

    app = tinyweb.webserver()

    # Index page
    @app.route('/')
    async def index(request, response):
        print(f"received request: {request.method} {request.path}")
        # Start HTTP response with content-type text/html
        await response.start_html()
        await response.send('<html><body><h1>Pico Weather</h1></html>\n')

    print(f"starting server on http://{ip}:80")
    # Register server task but don't run loop (loop_forever=False)
    # This allows us to share the event loop with other tasks
    app.run(host='0.0.0.0', port=80, loop_forever=False)
