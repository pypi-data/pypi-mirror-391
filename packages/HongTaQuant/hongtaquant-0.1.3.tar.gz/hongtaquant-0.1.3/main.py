from HongTaQuant import HongTaData


def main():
    print("Hello from hongtaquant!")
    client = HongTaData.HistoricalClient()
    client.connect()
    result = client.get_stock_data(period="min5", data_type="stock", start="20230101 09:30:00", end="20231231 15:00:00", symbols=["601236"], params="")
    print(len(result))


if __name__ == "__main__":
    main()
