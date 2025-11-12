from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="yfiles_graphs_for_streamlit",
    version="1.2.0",
    author="yWorks Support Team",
    author_email="yfileshtml@yworks.com",
    description="A diagram visualization component for Streamlit powered by yFiles for HTML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.yworks.com/products/yfiles-graphs-for-streamlit",
    license="See LICENSE.md",
    project_urls={
        "Homepage": "https://www.yworks.com/products/yfiles-graphs-for-streamlit",
        "License": "https://github.com/yWorks/yfiles-graphs-for-streamlit/blob/main/LICENSE.md",
        "Bug Tracker": "https://github.com/yWorks/yfiles-graphs-for-streamlit/issues",
        "Documentation": "https://github.com/yWorks/yfiles-graphs-for-streamlit/",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Topic :: Multimedia :: Graphics"
    ],
    keywords=[
        "Streamlit",
        "component",
        "yfiles",
        "visualization",
        "graph",
        "diagrams",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    # Ensure notices are also included in the wheel
    data_files=[
        ("notices", [
            "THIRD-PARTY-NOTICES.json",
            "THIRD-PARTY-NOTICES-RUNTIME.json",
            "REDISTRIBUTABLES.md",
        ])
    ],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
    ]
)
