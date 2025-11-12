import argparse
from reqsim.core import simulate

def main():
    parser = argparse.ArgumentParser(
        description="⚡ ReqSim — HTTP Request Simulator & Benchmark Tool"
    )
    parser.add_argument("url", help="Target URL")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of requests")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method")
    parser.add_argument("-d", "--data", help="Request body data")

    args = parser.parse_args()
    print(simulate(args.url, n=args.num, method=args.method, data=args.data))

if __name__ == "__main__":
    main()
