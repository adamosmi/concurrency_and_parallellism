def create_dotenv(remove=False):
    import os

    dotenv_fp = os.path.join("config", ".env")
    exists = os.path.isfile(dotenv_fp)

    if (not exists) or remove:
        SERVER_ADDRESS = input("Server address:\n")

        with open(dotenv_fp, "w") as f:
            f.write(f'SERVER_ADDRESS="{SERVER_ADDRESS.strip()}"')


if __name__ == "__main__":
    create_dotenv(remove=True)
