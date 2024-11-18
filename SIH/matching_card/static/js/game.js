class CardGame {
    constructor(roomId, playerId) {
        this.socket = new WebSocket(`ws://${window.location.host}/ws/game/${roomId}/`);
        this.playerId = playerId;
        this.currentCard = null;
        this.isPlayer1 = false;
        this.timer = new Timer(120, document.getElementById('timer'));
        this.setupWebSocket();
        this.setupEventListeners();
    }

    setupWebSocket() {
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleGameEvent(data);
        };
    }

    setupEventListeners() {
        document.getElementById('startButton')?.addEventListener('click', () => this.startGame());
        document.getElementById('drawButton').addEventListener('click', () => this.drawCard());
        document.getElementById('keepButton').addEventListener('click', () => this.keepCard());
        document.getElementById('discardButton').addEventListener('click', () => this.discardCard());
    }

    handleGameEvent(data) {
        switch(data.action) {
            case 'game_started':
                this.renderGameState(data.state);
                this.timer.start();
                document.getElementById('startButton')?.remove();
                break;
            case 'card_drawn':
                this.showDrawnCard(data.card);
                break;
            case 'turn_changed':
                this.updateTurn(data.current_player);
                break;
            case 'game_over':
                this.timer.stop();
                this.showGameOver(data.results);
                break;
        }
    }

    renderGameState(state) {
        this.isPlayer1 = this.playerId === state.players[0].id;
        
        const playerRole = document.getElementById('playerRole');
        playerRole.textContent = this.isPlayer1 ? 'Player 1' : 'Player 2';
        
        const myHand = this.isPlayer1 ? state.players[0] : state.players[1];
        const opponentHand = this.isPlayer1 ? state.players[1] : state.players[0];

        if (this.isPlayer1) {
            this.renderHand('player1Hand', myHand.cards);
            document.getElementById('player1Score').textContent = myHand.score;
            document.getElementById('player1Count').textContent = myHand.cards.length;
            document.getElementById('player2Count').textContent = opponentHand.cards.length;
            document.getElementById('player2Score').textContent = opponentHand.score;
        } else {
            this.renderHand('player2Hand', myHand.cards);
            document.getElementById('player2Score').textContent = myHand.score;
            document.getElementById('player2Count').textContent = myHand.cards.length;
            document.getElementById('player1Count').textContent = opponentHand.cards.length;
            document.getElementById('player1Score').textContent = opponentHand.score;
        }
    }

    renderHand(containerId, cards) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        cards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.innerHTML = `
                <h3>${card.case_name} (${card.year})</h3>
                <p>Article ${card.article_number}</p>
                <p>${card.description}</p>
            `;
            container.appendChild(cardElement);
        });
    }

    showDrawnCard(card) {
        this.currentCard = card;
        const cardContainer = document.getElementById('currentCard');
        cardContainer.innerHTML = `
            <div class="card description-card">
                <p>${card.description}</p>
            </div>
        `;
        document.getElementById('keepButton').disabled = false;
        document.getElementById('discardButton').disabled = false;
        document.getElementById('drawButton').disabled = true;
    }

    startGame() {
        this.socket.send(JSON.stringify({ action: 'start_game' }));
    }

    drawCard() {
        this.socket.send(JSON.stringify({
            action: 'draw_card',
            player_id: this.playerId
        }));
    }

    keepCard() {
        this.socket.send(JSON.stringify({
            action: 'keep_card',
            player_id: this.playerId,
            card: this.currentCard
        }));
    }

    discardCard() {
        this.socket.send(JSON.stringify({
            action: 'discard_card',
            player_id: this.playerId,
            card: this.currentCard
        }));
    }

    showGameOver(results) {
        const gameOver = document.getElementById('gameOver');
        const winner = document.getElementById('winner');
        const finalScores = document.getElementById('finalScores');
        
        gameOver.classList.remove('hidden');
        winner.textContent = `Winner: ${results.winner}`;
        finalScores.textContent = `Final Scores - Player 1: ${results.scores.player1}, Player 2: ${results.scores.player2}`;
    }
}

class Timer {
    constructor(duration, display) {
        this.duration = duration;
        this.display = display;
        this.running = false;
        this.remainingTime = duration;
    }

    start() {
        if (this.running) return;
        this.running = true;
        this.tick();
    }

    tick() {
        if (!this.running) return;
        
        const minutes = Math.floor(this.remainingTime / 60);
        const seconds = this.remainingTime % 60;
        
        this.display.textContent = `Time: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        if (this.remainingTime <= 0) {
            this.stop();
            return;
        }
        
        this.remainingTime--;
        setTimeout(() => this.tick(), 1000);
    }

    stop() {
        this.running = false;
    }
}