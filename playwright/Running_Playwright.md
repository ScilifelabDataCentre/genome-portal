

### Overview 

- [Playwright](https://playwright.dev/python/) is used to test the website functionality. 

- Tests are split up per webpage, with the Playwright Page objects created as pytest fixtures inside of `conftest.py`. 

- To test the species-specific webpages, each page type (introduction, assembly, download) for every species is tested using the same set of tests. 

- This is acheived by looking up all the species present (with pathlib) and creating a list of Page objects for each page type (one page per species).

- The tests are then run using a for loop on each page type (e.g. assembly). New species are therefore added automatically with this approach. 


### To run the tests locally 

**1. Install playwright and it's requirements:**

```bash
pip install -r requirements.txt
```

**2. Start running a local version of the server:**

```bash
cd hugo
hugo server
```

**3. Run the tests**

Run playwright:
```bash
pytest playwright/tests/ --base-url http://localhost:1313 
```

Note: if you want to run the tests in parralel using playwright you can add the flag `--numprocesses auto`

```bash
pytest playwright/tests/ --base-url http://localhost:1313 --numprocesses auto
```