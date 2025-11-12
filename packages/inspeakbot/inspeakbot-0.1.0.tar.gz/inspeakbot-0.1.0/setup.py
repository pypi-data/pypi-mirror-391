
from setuptools import setup, find_packages

setup(
    name='inspeakbot',         # الاسم الذي سيتم تحميل المكتبة به (pip install)
    version='0.1.0',            # رقم الإصدار الأولي
    packages=find_packages(),
    install_requires=[         # المكتبات التي يعتمد عليها كودك
        'requests',
    ],
    author='Karim Mohamed',
    author_email='KimoDeveloper@levelupstudios.xyz',
    description='Official Python SDK for InSpeak Bot API .',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://inspeak.levelupstudios.xyz',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
