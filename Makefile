PY = venv\Scripts\python

clean:
	$(PY) -m pyclean .

run:
	$(PY) -m uvicorn main:app --reload

reqs:
	$(PY) -m poetry export -f requirements.txt --output requirements.txt --without-hashes
