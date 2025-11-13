from setuptools import setup, find_packages

setup(
    name="viswanth",
    version="1.0.0",
    author="Viswanth S S",
    author_email="viswanth@example.com",
    description="Offline Conversational AI Lab Experiments (7–10)",
    long_description="This package contains Conversational AI experiments including Chatbot, Voice Bot, Classroom Bot, and Medical Bot. Works offline for university labs.",
    long_description_content_type="text/plain",
    packages=find_packages(),
    install_requires=["flask", "nltk", "pyttsx3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
