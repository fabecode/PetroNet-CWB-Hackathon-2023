@echo off

rem set values for your Search service (from .env file)
for /f "usebackq tokens=1,2 delims== " %%G in (".env") do (
    set "%%G=%%H"
)

echo -----
echo Updating the skillset...
call curl -X PUT %url%/skillsets/cwb-petronas-final-skillset?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-skillset.json

rem wait
timeout /t 2 /nobreak

echo -----
echo Updating the index...
call curl -X PUT %url%/indexes/cwb-petronas-final-index?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-index.json

rem wait
timeout /t 2 /nobreak

echo -----
echo Updating the indexer...
call curl -X PUT %url%/indexers/cwb-petronas-final-indexer?api-version=2020-06-30 -H "Content-Type: application/json" -H "api-key: %admin_key%" -d @search-indexer.json

echo -----
echo Resetting the indexer
call curl -X POST %url%/indexers/cwb-petronas-final-indexer/reset?api-version=2020-06-30 -H "Content-Type: application/json" -H "Content-Length: 0" -H "api-key: %admin_key%" 

rem wait
timeout /t 5 /nobreak

echo -----
echo Rerunning the indexer
call curl -X POST %url%/indexers/cwb-petronas-final-indexer/run?api-version=2020-06-30 -H "Content-Type: application/json" -H "Content-Length: 0" -H "api-key: %admin_key%" 
