# ImpactEcho

Blockchain-backed donation platform built at the HackOween hackathon (top 4). Donors give to NGO
causes and get a verifiable record of every transaction. NGOs register, are approved by an admin,
and request funding against their causes. Built by a team of two: Aditya Singhal and Manaswi Guntupalli.

## Features

- **Donors:** register with email and password, get an automatically created wallet (no crypto
  knowledge needed), donate in INR, view transaction history and receipts
- **Custom ledger:** a Python blockchain with wallets, mining, block explorer endpoints and chain
  verification (`inr_blockchain.py`, `inr_wallet.py`, `blockchain_wallet.py`)
- **NGOs:** registration, admin approval, credential creation, cause requests, donation view and
  notifications
- **Admin:** approves NGOs and causes, handles deletion requests, tracks blockchain activity
- **Smart contracts:** Foundry project with a `FundMe` crowdfunding contract and Chainlink-style
  price conversion (`foundry/`)
- **Frontend:** HTML, CSS and JavaScript with an in-page chatbot

## Stack

Python, Flask, JSON file storage, Solidity (Foundry), HTML, CSS, JavaScript

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Runtime data files (users, NGO records, donation logs, wallets) are created on first run and are
git-ignored. Do not commit them.

## Notes

This is hackathon code, so treat it as a demo. Set `SECRET_KEY`, `ADMIN_USER` and `ADMIN_PASSWORD`
in the environment before running anywhere public; the defaults are for local use only. Data is stored
in JSON files.
