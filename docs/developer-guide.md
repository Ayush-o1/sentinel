# Developer Guide

Welcome to the SENTINEL codebase. This guide outlines how to contribute to the project.

## Adding a New API Endpoint
1. **Define Schema**: Open `app/schemas/` and define the incoming Pydantic request model and outgoing response model.
2. **Database (Optional)**: If storing new data, add the model to `app/models/` and run `alembic revision --autogenerate -m "Added X"`.
3. **Repository**: Create or update a repository in `app/repositories/` to handle the specific SQLAlchemy `Select` or `Insert` query.
4. **Service**: Add the business logic to `app/services/`.
5. **Router**: Create the endpoint in `app/api/v1/`. Use `Depends()` to inject your Service. Update `app/api/v1/router.py` to include your new file if necessary.

## Retraining the ML Model
If you want to train the model on a different dataset or try a new algorithm:
1. Replace or update the dataset in `ml/data/raw/`.
2. Ensure you are in the Python virtual environment (`backend/.venv`).
3. Run the training script: `python -m app.ml.train`.
4. The script will automatically compare algorithms, select the best one, and overwrite `app/ml/models/sentinel_v1.0.0.joblib`.
5. Restart the FastAPI server so the new model is loaded via the lifespan event.

## Adding a New Frontend Page
1. **Create Component**: Add your new view inside `frontend/src/pages/MyNewPage.tsx`.
2. **Update Router**: Open `frontend/src/App.tsx` and add a new `<Route>` definition. Use the `<ProtectedRoute>` wrapper if the page requires authentication.
3. **Sidebar**: Update `frontend/src/components/layout/Sidebar.tsx` to include a navigation link to your new page.

## Database Migrations
Never use `Base.metadata.create_all()` to alter the database schema.
Whenever you modify a class in `app/models/`, you must generate an Alembic migration:
```bash
cd backend
alembic revision --autogenerate -m "Describe your schema change"
alembic upgrade head
```

## Coding Standards
- **Python**: Enforce typing strictly (`-> dict`, `: str`). Format code using `black` and `ruff`.
- **TypeScript**: Avoid `any`. Define strictly typed interfaces in `frontend/src/types/index.ts`. Format with `eslint` (or `oxlint`).
- **Commits**: Use conventional commits (e.g., `feat: added analytics chart`, `fix: corrected LIME token weights`).
