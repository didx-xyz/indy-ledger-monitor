FROM bcgovimages/von-image:next-1

RUN pip install pynacl gspread oauth2client pickledb tinydb graphene fastapi uvicorn

# ADD fetch_ledger_tx.py .
ADD networks.json .
ADD *.py ./

ENTRYPOINT ["bash", "-c", "python fetch_ledger_tx.py $@", "--"]
