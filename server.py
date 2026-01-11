from config import Config
from display import DisplayController
from font_renderer import FontSize
from net import NetworkManager, connect_to_network
from lib import tinyweb

def start_server(config: Config, net: NetworkManager, display: DisplayController):
    # there's no corresponding net.return_net() call
    # because the connection has to stay up
    ip = connect_to_network(net, display)

    app = tinyweb.webserver()

    # Index page
    @app.route('/')
    async def index(request, response):
        print(f"received request: {request.method} {request.path}")
        try:
            await response.send_file('www/index.html', content_type='text/html', max_age=0)
        except tinyweb.HTTPException as e:
            if e.code == 404:
                await response.start_html()
                await response.send('<html><body><h1>Pico Weather</h1><p>Error: index.html not found</p></body></html>\n')
            else:
                raise

    port = config.listen_port

    print(f"starting server on http://{ip}:{port}")
    # Register server task but don't run loop (loop_forever=False)
    # This allows us to share the event loop with other tasks
    app.run(host='0.0.0.0', port=port, loop_forever=False)
