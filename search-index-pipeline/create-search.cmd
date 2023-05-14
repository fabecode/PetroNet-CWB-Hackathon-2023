@echo off

rem set values for your search service (from .env file)
for /f "usebackq tokens=1,2 delims== " %%G in (".env") do (
    set "%%G=%%H"
)

echo -----
echo Creating the data source...
call curl -X POST %url%/datasources?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-datasource.json

rem wait
timeout /t 3 /nobreak

echo -----
echo Creating the skillset...
call curl -X PUT %url%/skillsets/cwb-petronas-final-skillset?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-skillset.json

rem wait
timeout /t 3 /nobreak

echo -----
echo Creating the index...
call curl -X PUT %url%/indexes/cwb-petronas-final-index?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-index.json

rem wait
timeout /t 5 /nobreak

echo -----
echo Creating the indexer...
call curl -X PUT %url%/indexers//cwb-petronas-final-indexer?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-indexer.json