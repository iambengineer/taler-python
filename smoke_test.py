from taler_python.clients.merchant import MerchantClient

with MerchantClient("https://backend.demo.taler.net") as client:
    config = client.get_config()
    print(config)