import argparse

from vertex_gemini import call_vertex_gemini


def parse_args():
    parser = argparse.ArgumentParser(description="Vertex Gemini smoke test using ADC.")
    parser.add_argument("--prompt", default="Explain AI in one sentence.")
    parser.add_argument("--model", help="Vertex model name (default: env VERTEX_MODEL or gemini-2.0-flash).")
    parser.add_argument("--project", help="GCP project id (default: env VERTEX_PROJECT or gcloud config).")
    parser.add_argument("--location", help="Vertex location (default: env VERTEX_LOCATION or us-central1).")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    response = call_vertex_gemini(
        args.prompt,
        model=args.model,
        project=args.project,
        location=args.location,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        log_fn=print,
    )
    if not response:
        raise SystemExit("Vertex Gemini returned no response.")
    print(response)


if __name__ == "__main__":
    main()
