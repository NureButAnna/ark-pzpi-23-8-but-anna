from fastapi import FastAPI
from src.api import users, containers, organizations, disposal_requests
from src.api import auth, client_companies, vehicles, container_sites
from src.api import admin, pickups, analytics, doc


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
app.include_router(admin.router)
app.include_router(disposal_requests.router)
app.include_router(pickups.router)
app.include_router(doc.router)
app.include_router(analytics.router)
