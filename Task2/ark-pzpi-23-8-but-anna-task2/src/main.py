from fastapi import FastAPI
from src.api import users, containers, organizations, auth, client_companies, vehicles, container_sites


app = FastAPI(
    title="Ecofy 🍀 ",
    description="Ecofy — система для управління утилізацією та вивезенням відходів",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(client_companies.router)
app.include_router(organizations.router)
app.include_router(containers.router)
app.include_router(container_sites.router)
app.include_router(vehicles.router)
