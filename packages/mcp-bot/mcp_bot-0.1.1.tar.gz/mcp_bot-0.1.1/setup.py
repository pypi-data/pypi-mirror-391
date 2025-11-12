from setuptools import setup, find_packages

setup(
    name='mcp-bot',
    version='0.1.1',
    author='Nilavo Boral',
    author_email='nilavoboral@gmail.com',
    description='An interactive chat UI for communicating with your MCP Tools via AI Agents.',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/NilavoBoral/mcp-bot",
    project_urls={
        "LinkedIn": "https://www.linkedin.com/in/nilavo-boral-123bb5228/",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit==1.49.1',
        'langchain==1.0.5',
        'langchain-core==1.0.4',
        'langchain-google-genai==3.0.1',
        'langchain-mcp-adapters==0.1.12',
        'nest_asyncio==1.6.0',
    ],
    entry_points={
        'console_scripts': [
            'mcp-bot = mcp_bot.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.11',
)
