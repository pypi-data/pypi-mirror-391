from setuptools import setup, find_packages

# Carregando a descrição longa do arquivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whats77",  # Nome do pacote
    version="0.1.3",
    author="Vinicius Moreira",
    author_email="vinicius@77indicadores.com.br",
    description="Facilitador para uso da API WhatsApp (ZAPI)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/77-Indicadores/modulo_whatsapp",
    packages=find_packages(),  # Detecta automaticamente os pacotes
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Define a versão mínima do Python
    install_requires=[
        "requests>=2.0.0",  # Dependência necessária para o funcionamento
        "python-dotenv>=0.21.0",  # Incluindo dotenv para carregar variáveis de ambiente
    ]
)
