import random

# ==========================================
# 1. Deck & Card Architecture
# ==========================================
class Card:
    def __init__(self, rank, suit):
        self.rank = rank # '2'-'9', 'T', 'J', 'Q', 'K', 'A'
        self.suit = suit # 'C', 'D', 'H', 'S'

    def get_value(self, game_type="blackjack"):
        if game_type == "baccarat":
            if self.rank in ['T', 'J', 'Q', 'K']: return 0
            if self.rank == 'A': return 1
            return int(self.rank)
            
        # Blackjack values
        if self.rank in ['T', 'J', 'Q', 'K']: return 10
        if self.rank == 'A': return 11 # Handled dynamically in scoring
        return int(self.rank)

    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Shoe:
    def __init__(self, num_decks=6, penetration=0.75):
        self.num_decks = num_decks
        self.penetration = penetration
        self.cards = []
        self.shuffle()

    def shuffle(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['C', 'D', 'H', 'S']
        self.cards = [Card(r, s) for r in ranks for s in suits] * self.num_decks
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) < (52 * self.num_decks * (1 - self.penetration)):
            self.shuffle()
        return self.cards.pop()

# ==========================================
# 2. Betting Strategies
# ==========================================
class BettingStrategy:
    def __init__(self, bankroll, base_unit=10):
        self.bankroll = bankroll
        self.profit = 0
        self.base_unit = base_unit
        self.current_bet = base_unit

    def observe_card(self, card):
        """Hook for card counting strategies to track dealt cards."""
        pass 

    def update_after_result(self, net_win):
        self.bankroll += net_win
        self.profit += net_win
        self._adjust_bet(net_win)

    def _adjust_bet(self, net_win):
        """Override this in subclasses to change bet sizing."""
        pass
        
    def get_bet(self):
        # Prevent betting more than the bankroll (optional realism)
        return min(self.current_bet, self.bankroll) if self.bankroll > 0 else 0

class FlatBetting(BettingStrategy):
    # Bet size never changes
    pass

class Martingale(BettingStrategy):
    def _adjust_bet(self, net_win):
        if net_win > 0:
            self.current_bet = self.base_unit
        elif net_win < 0:
            self.current_bet *= 2

class Fibonacci(BettingStrategy):
    def __init__(self, bankroll, base_unit=10, is_positive=False):
        super().__init__(bankroll, base_unit)
        self.sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
        self.index = 0
        self.is_positive = is_positive

    def _adjust_bet(self, net_win):
        if net_win == 0: return # Push doesn't change sequence
        won = net_win > 0
        
        # Positive: Step up on win, step down 2 on loss
        # Negative: Step up on loss, step down 2 on win
        move_up = won if self.is_positive else not won

        if move_up:
            self._lose_bet()
        else:
            self._win_bet()
            
        self.current_bet = self.base_unit * self.sequence[self.index]
    
    def _lose_bet(self):
        self.index = min(self.index + 1, len(self.sequence) - 1)
    def _win_bet(self):
        self.index = max(self.index - 2, 0)

class PositiveStableFibonacci(Fibonacci):
    def __init__(self, bankroll, base_unit=10, is_positive=False):
        super().__init__(bankroll, base_unit, is_positive)
        self.sequence.insert(0, 1)
    def _win_bet(self):
        self.index = 0
    

class HiLoCounting(BettingStrategy):
    def __init__(self, bankroll, base_unit=10, shoe_ref=None):
        super().__init__(bankroll, base_unit)
        self.shoe = shoe_ref
        self.running_count = 0

    def observe_card(self, card):
        if card.rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif card.rank in ['T', 'J', 'Q', 'K', 'A']:
            self.running_count -= 1

    def _adjust_bet(self, net_win):
        # Update bet purely based on true count, ignoring last win/loss
        cards_remaining = len(self.shoe.cards)
        decks_remaining = max(1, cards_remaining / 52.0)
        true_count = int(self.running_count / decks_remaining)

        if true_count <= 0:
            self.current_bet = self.base_unit
        else:
            # Bet spread: Increase by 1 unit per True Count
            self.current_bet = self.base_unit + (true_count * self.base_unit)

# ==========================================
# 3. Game Engines
# ==========================================
class BaccaratSimulator:
    def __init__(self, strategy: BettingStrategy, shoe: Shoe):
        self.shoe = shoe
        self.strategy = strategy

    def baccarat_score(self, hand):
        return sum(card.get_value("baccarat") for card in hand) % 10

    def draw_and_observe(self):
        card = self.shoe.draw()
        self.strategy.observe_card(card)
        return card

    def play_round(self):
        bet_amount = self.strategy.get_bet()
        if bet_amount <= 0: return # Bankrupt
        
        # Always bet Banker for lowest house edge
        bet_choice = 'Banker' 
        
        player_hand = [self.draw_and_observe(), self.draw_and_observe()]
        banker_hand = [self.draw_and_observe(), self.draw_and_observe()]
        
        p_score = self.baccarat_score(player_hand)
        b_score = self.baccarat_score(banker_hand)
        
        # Third card rules
        if p_score not in (8, 9) and b_score not in (8, 9):
            if p_score <= 5:
                third_card = self.draw_and_observe()
                player_hand.append(third_card)
                p_score = self.baccarat_score(player_hand)
                p_third_val = third_card.get_value("baccarat")
            else:
                p_third_val = None
            
            if p_third_val is None:
                if b_score <= 5: banker_hand.append(self.draw_and_observe())
            else:
                if b_score <= 2: banker_hand.append(self.draw_and_observe())
                elif b_score == 3 and p_third_val != 8: banker_hand.append(self.draw_and_observe())
                elif b_score == 4 and p_third_val in (2,3,4,5,6,7): banker_hand.append(self.draw_and_observe())
                elif b_score == 5 and p_third_val in (4,5,6,7): banker_hand.append(self.draw_and_observe())
                elif b_score == 6 and p_third_val in (6,7): banker_hand.append(self.draw_and_observe())
            
            b_score = self.baccarat_score(banker_hand)

        # Resolution
        win_amount = -bet_amount
        if p_score > b_score:
            if bet_choice == 'Player': win_amount = bet_amount
        elif b_score > p_score:
            if bet_choice == 'Banker': win_amount = bet_amount * 0.95 # 5% commission
        else:
            if bet_choice == 'Tie': win_amount = bet_amount * 8
            else: win_amount = 0 # Push

        self.strategy.update_after_result(win_amount)

class BlackjackSimulator:
    def __init__(self, strategy: BettingStrategy, shoe: Shoe):
        self.shoe = shoe
        self.strategy = strategy

    def bj_score(self, hand):
        score = sum(card.get_value("blackjack") for card in hand)
        aces = sum(1 for card in hand if card.rank == 'A')
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        return score

    def draw_and_observe(self):
        card = self.shoe.draw()
        self.strategy.observe_card(card)
        return card

    def get_action(self, player_hand, dealer_upcard):
        # Simplified Basic Strategy
        score = self.bj_score(player_hand)
        d_val = dealer_upcard.get_value("blackjack")
        
        if score < 12: return 'H'
        if score == 11: return 'D' # Simplified Double logic
        if score > 16: return 'S'
        if d_val > 6: return 'H'
        return 'S'

    def play_round(self):
        bet_amount = self.strategy.get_bet()
        if bet_amount <= 0: return # Bankrupt
        
        player_hand = [self.draw_and_observe(), self.draw_and_observe()]
        dealer_hand = [self.draw_and_observe(), self.draw_and_observe()]
        dealer_upcard = dealer_hand[0]

        p_score = self.bj_score(player_hand)
        d_score = self.bj_score(dealer_hand)

        # Blackjack Check
        if p_score == 21 and d_score != 21:
            self.strategy.update_after_result(bet_amount * 1.5)
            return
        elif p_score == 21 and d_score == 21:
            self.strategy.update_after_result(0)
            return
        elif d_score == 21:
            self.strategy.update_after_result(-bet_amount)
            return

        # Player Turn
        multiplier = 1
        while True:
            action = self.get_action(player_hand, dealer_upcard)
            if action == 'H':
                player_hand.append(self.draw_and_observe())
                if self.bj_score(player_hand) > 21:
                    self.strategy.update_after_result(-bet_amount)
                    return
            elif action == 'D':
                multiplier = 2
                player_hand.append(self.draw_and_observe())
                break # Forced stand
            else: # Stand
                break

        p_score = self.bj_score(player_hand)
        if p_score > 21:
            self.strategy.update_after_result(-bet_amount * multiplier)
            return

        # Dealer Turn (Hits soft 17)
        while self.bj_score(dealer_hand) < 17:
            dealer_hand.append(self.draw_and_observe())
            
        d_score = self.bj_score(dealer_hand)
        net_bet = bet_amount * multiplier

        if d_score > 21 or p_score > d_score:
            self.strategy.update_after_result(net_bet)
        elif d_score > p_score:
            self.strategy.update_after_result(-net_bet)
        else:
            self.strategy.update_after_result(0)

def simulate(strat, r=100):
    # 1. Test Baccarat with Negative Fibonacci
    bac_shoe = Shoe(num_decks=8)
    bac_strat = strat
    bac_game = BaccaratSimulator(bac_strat, bac_shoe)
    
    for _ in range(r): 
        bac_game.play_round()
    print(f"Baccarat ({bac_strat.__class__.__name__}): Bankroll = ${bac_strat.bankroll:.2f} | Profit = ${bac_strat.profit:.2f}")

# ==========================================
# 4. Running the Tests
# ==========================================
if __name__ == "__main__":
    ROUNDS = 1000
    STARTING_BANKROLL = 5000
    BASE_UNIT = 10
    
    print(f"--- Simulating {ROUNDS} hands ---")

    simulate(FlatBetting(STARTING_BANKROLL,BASE_UNIT),ROUNDS)

    # 1. Test Baccarat with Negative Fibonacci
    bac_shoe = Shoe(num_decks=8)
    bac_strat = PositiveStableFibonacci(STARTING_BANKROLL, BASE_UNIT, is_positive=True)
    bac_game = BaccaratSimulator(bac_strat, bac_shoe)
    
    for _ in range(ROUNDS): 
        bac_game.play_round()
    print(f"Baccarat (Fibonacci): Bankroll = ${bac_strat.bankroll:.2f} | Profit = ${bac_strat.profit:.2f}")

    # 2. Test Blackjack with Hi-Lo Card Counting
    bj_shoe = Shoe(num_decks=6)
    bj_strat = HiLoCounting(STARTING_BANKROLL, BASE_UNIT, shoe_ref=bj_shoe)
    bj_game = BlackjackSimulator(bj_strat, bj_shoe)
    
    for _ in range(ROUNDS): 
        bj_game.play_round()
    print(f"Blackjack (Hi-Lo Counting): Bankroll = ${bj_strat.bankroll:.2f} | Profit = ${bj_strat.profit:.2f}")