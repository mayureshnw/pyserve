from src.runner import Server


def main():
    server = Server('', 8888)
    server.run()


if __name__ == '__main__':
    main()
