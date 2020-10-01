FROM bcgovimages/von-image:next-1

RUN pip install pynacl

ADD fetch_ledger_tx.py .
ADD networks.json .

ENTRYPOINT ["bash", "-c", "python fetch_ledger_tx.py $@", "--"]
