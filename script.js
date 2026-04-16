const computerHand = document.getElementById('computer-hand');
const playerHand = document.getElementById('player-hand');
const computerChoiceText = document.getElementById('computer-choice');
const playerChoiceText = document.getElementById('player-choice');
const feedbackText = document.getElementById('feedback-text');
const controls = document.getElementById('controls');
const playerScoreSpan = document.getElementById('player-score');
const computerScoreSpan = document.getElementById('computer-score');
const tieScoreSpan = document.getElementById('tie-score');
const controlButtons = Array.from(controls.querySelectorAll('button'));

const choices = ['rock', 'paper', 'scissors'];
const RESULT_DELAY_MS = 2000;
const handImages = {
    computer: {
        rock: 'public/stoneComputer.png',
        paper: 'public/paperComputer.png',
        scissors: 'public/scissorsComputer.png'
    },
    player: {
        rock: 'public/stonePlayer.png',
        paper: 'public/paperPlayer.png',
        scissors: 'public/scissorsPlayer.png'
    }
};

let playerScore = 0;
let computerScore = 0;
let tieScore = 0;
let isRoundLocked = false;

controls.addEventListener('click', (event) => {
    if (event.target.tagName !== 'BUTTON') {
        return;
    }

    if (event.target.id === 'reset') {
        resetGame();
        return;
    }

    const playerChoice = event.target.dataset.choice;
    if (!choices.includes(playerChoice)) {
        return;
    }

    playRound(playerChoice);
});

function playRound(playerChoice) {
    if (isRoundLocked) {
        return;
    }

    isRoundLocked = true;
    setControlsDisabled(true);
    setHandsShaking(true);
    feedbackText.textContent = 'Hands are shaking...';
    computerChoiceText.textContent = '...';
    playerChoiceText.textContent = '...';

    const computerChoice = choices[Math.floor(Math.random() * 3)];

    window.setTimeout(() => {
        updateHands(playerChoice, computerChoice);
        setHandsShaking(false);

        if (playerChoice === computerChoice) {
            tieScore += 1;
            feedbackText.textContent = `Tie. Both picked ${playerChoice}.`;
        } else if (
            (playerChoice === 'rock' && computerChoice === 'scissors') ||
            (playerChoice === 'paper' && computerChoice === 'rock') ||
            (playerChoice === 'scissors' && computerChoice === 'paper')
        ) {
            playerScore += 1;
            feedbackText.textContent = `You win this round. ${playerChoice} beats ${computerChoice}.`;
        } else {
            computerScore += 1;
            feedbackText.textContent = `Computer wins this round. ${computerChoice} beats ${playerChoice}.`;
        }

        updateScore();
        setControlsDisabled(false);
        isRoundLocked = false;
    }, RESULT_DELAY_MS);
}

function updateHands(playerChoice, computerChoice) {
    computerHand.src = handImages.computer[computerChoice];
    playerHand.src = handImages.player[playerChoice];

    computerHand.alt = `Computer hand showing ${computerChoice}`;
    playerHand.alt = `Player hand showing ${playerChoice}`;

    computerChoiceText.textContent = computerChoice;
    playerChoiceText.textContent = playerChoice;
}

function updateScore() {
    playerScoreSpan.textContent = playerScore;
    computerScoreSpan.textContent = computerScore;
    tieScoreSpan.textContent = tieScore;
}

function setHandsShaking(isShaking) {
    computerHand.classList.toggle('shaking-left', isShaking);
    playerHand.classList.toggle('shaking-right', isShaking);
}

function setControlsDisabled(isDisabled) {
    controlButtons.forEach((button) => {
        button.disabled = isDisabled;
    });
    controls.classList.toggle('disabled', isDisabled);
}

function resetGame() {
    isRoundLocked = false;
    playerScore = 0;
    computerScore = 0;
    tieScore = 0;

    setHandsShaking(false);
    setControlsDisabled(false);
    updateHands('rock', 'rock');
    updateScore();
    feedbackText.textContent = 'Game reset. Pick your next move.';
}

resetGame();
 