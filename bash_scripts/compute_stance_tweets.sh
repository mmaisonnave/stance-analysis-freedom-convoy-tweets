
SAMPLE_SIZE=5000
REPOSITORY_PATH="/Users/marianomaisonnave/Repositories/stance-analysis-freedom-convoy-tweets"
VENV_PATH="${REPOSITORY_PATH}/.venv"
SCRIPT=${REPOSITORY_PATH}/scripts/evaluate_stance_tweets.py

echo REPO\\tPATH:\\t${REPOSITORY_PATH}
echo VENV\\tPATH:\\t${VENV_PATH}
echo SCRIPT\\tPATH:\\t${SCRIPT}

# Loading the virtual environment
source ${VENV_PATH}/bin/activate

echo WHICH\\tPYTHON:\\t$(which python)

echo
echo "COUNTING COMPUTED TWEETS BEFORE EXECUTION"
python $SCRIPT --count

echo
echo PREPARING TO COMPUTE STANCE ON ${SAMPLE_SIZE} TWEETS...
python $SCRIPT --compute --sample-size ${SAMPLE_SIZE}

echo
echo "COUNTING COMPUTED TWEETS AFTER EXECUTION"
python $SCRIPT --count