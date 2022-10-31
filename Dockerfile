FROM python:slim-buster AS builder

WORKDIR /opt/
COPY . .
RUN pip3 install --no-cache --upgrade -r requirements.txt
RUN apt-get update
RUN apt-get install -y binutils libc-bin
RUN pyinstaller scripts/tagvalidator.py --onefile

FROM python:slim-buster AS deployer
WORKDIR /opt
COPY --from=builder /opt/dist/tagvalidator /usr/local/bin/tagvalidator
ENTRYPOINT ["/usr/local/bin/tagvalidator","-p" , "tagvalidator.yml", "-r", "."]