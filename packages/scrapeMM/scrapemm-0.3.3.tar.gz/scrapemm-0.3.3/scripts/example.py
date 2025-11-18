from scrapemm import retrieve
import asyncio

if __name__ == "__main__":
    url = "https://factuel.afp.com/doc.afp.com.43ZN7NP"
    result = asyncio.run(retrieve(url, methods=["decodo"]))
    print(result)
