import os
from dotenv import load_dotenv

load_dotenv()

def get_cfg():
    return {
        "langfuse_public": os.getenv("LANGFUSE_PUBLIC_KEY"),
        "langfuse_secret": os.getenv("LANGFUSE_SECRET_KEY"),
        "langfuse_endpoint": os.getenv("LANGFUSE_ENDPOINT") 
            or os.getenv("LANGFUSE_OTLP_ENDPOINT")
            or os.getenv("LANGFUSE_TRACE_URL"),

        "aws_sqs_url": os.getenv("AWS_SQS_OTEL"),
        "env": os.getenv("ENV", "dev"),
        "project": os.getenv("PROJECT", "genai-app"),

        "aws_profile": os.getenv("AWS_PROFILE", None),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
    }
