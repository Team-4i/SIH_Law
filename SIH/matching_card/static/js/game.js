class CardGame {
    constructor(roomId, playerId) {
        this.socket = new WebSocket(`ws://${window.location.host}/ws/game/${roomId}/`);
        this.playerId = playerId;
        this.currentCard = null;
        this.isPlayer1 = false;
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
                break;
            case 'card_drawn':
                this.showDrawnCard(data.card);
                break;
            case 'turn_changed':
                this.updateTurn(data.current_player);
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
            cardElement.textContent = `Article ${card.number}`;
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
}