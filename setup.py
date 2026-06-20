from setuptools import setup, find_packages

setup(
    name='arbiter-lite',
    version='0.1.0',
    description='Multi-Agent Context Quota Manager + Diagnostic Tool — 40 lines, zero dependencies',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='qiushu-wq',
    url='https://github.com/qiushu-wq/arbiter',
    packages=find_packages(),
    py_modules=['arbiter_doctor', 'stability_metrics'],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'arbiter-doctor=arbiter_doctor:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='agent, llm, context, quota, multi-agent, diagnostic',
)
