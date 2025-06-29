FROM python:3.10
WORKDIR /root/fw3
RUN apt update &&\
apt install screen locales -y &&\
echo "LC_ALL=en_US.UTF-8" >> /etc/environment &&\
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen &&\
echo "LANG=en_US.UTF-8" > /etc/locale.conf &&\
locale-gen en_US.UTF-8
ENV PYTHONPATH "/root/fw3/"
ENV PYTHONUTF8 1
ENV TZ=Europe/Minsk
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install poetry
# Copy only pyproject.toml first
COPY pyproject.toml ./
# Generate a fresh lock file based on pyproject.toml
RUN poetry lock
# Now install dependencies
RUN poetry install --only main --extras linux --no-root
COPY . ./
CMD ["bash"]