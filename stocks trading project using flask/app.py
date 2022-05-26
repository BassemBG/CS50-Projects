import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = db.execute("SELECT * FROM users_stocks WHERE user_id = ? ORDER BY shares DESC",session["user_id"])
    #get stock's name and current price
    stocks_total = 0
    for stock in stocks :
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = stock["price"] * stock["shares"]
        stocks_total = stocks_total + stock["total"]
    #get user's cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?",session["user_id"])[0]["cash"]
    return render_template("index.html",stocks=stocks,stocks_total=stocks_total,cash=cash)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST" :
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        if not symbol :
            return apology("must provide symbol")
        if not lookup(symbol):
            return apology("symbol doesn't exist")
        if shares < 0 :
            return apology("number of shares can't be negative")
        cash = db.execute("SELECT cash FROM users WHERE id = ?",session["user_id"])[0]["cash"]
        price = lookup(symbol)["price"]
        if cash < price*shares :
            return apology("You cannot afford the number of shares with current price")

        #check if we already bought this stock or no
        already_bought = db.execute("SELECT * FROM users_stocks WHERE user_id = ? AND symbol = ? AND shares > 0",
        session["user_id"], symbol)

        #if we did ,update number of shares
        if already_bought:
            db.execute("UPDATE users_stocks set shares = shares + ? WHERE symbol = ? AND user_id = ?",
        shares, symbol, session["user_id"])

        #else we didn't /or sold all of it , insert new data
        else:
            db.execute("INSERT INTO users_stocks (user_id, symbol, shares) VALUES(?, ?, ?)",
        session["user_id"], symbol, shares)

        #update transactions history
        db.execute("INSERT INTO purchase (buyer_id,symbol,price,shares) VALUES(?,?,?,?)",session["user_id"],symbol,price,shares)

        #update cash balance
        db.execute("UPDATE users SET cash=? WHERE id=?",cash-(price*shares),session["user_id"])

        return redirect("/")
    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM purchase WHERE buyer_id = ? ORDER BY date_time ASC",session["user_id"])
    return render_template("history.html",history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST" :
        symbol = request.form.get("symbol")
        if not symbol :
            return apology("must provide stock's symbol!")
        if not lookup(symbol):
            return apology("symbol not found")
        return render_template("quoted.html",quote=lookup(symbol))

    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #user reached via POST .He submitted the form
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        #check if all the form is filled
        if not username or not password or not confirm :
            return apology("Fill in all the blanks! ")
        #check if password and confirmation match
        if password != confirm :
            return apology("Passwords don't match! ")
        #check if username already exists
        if db.execute("SELECT * FROM users WHERE username=?",username):
            return apology("Username already exists! ")
        #add new user to database
        db.execute("INSERT INTO users (username,hash) VALUES(?,?)",username,generate_password_hash(password))
        #take new user to login
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        #check if symbol is chosen
        if not symbol :
            return apology("pick a stock to sell")

        #check if we have shares for this stock to sell
        stock_shares = db.execute("SELECT shares FROM users_stocks WHERE user_id = ? AND symbol = ? and shares > 0",
        session["user_id"], symbol)
        if not stock_shares :
            return apology("there are no shares to sell")

        #check if shares are positive
        if shares < 0 :
            return apology("number of shares can't be negative")

        #check if shares to sell aren't more than what the user has
        if shares > stock_shares[0]["shares"] :
            return apology("Can't sell more shares than you have")

        #update shares
        db.execute("UPDATE users_stocks set shares = shares - ? WHERE symbol = ? AND user_id = ?",
        shares, symbol, session["user_id"])

        #update cash
        curr_price = lookup(symbol)["price"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", curr_price*shares, session["user_id"])

        #update transactions history
        db.execute("INSERT INTO purchase (buyer_id,symbol,price,shares) VALUES(?,?,?,?)",
        session["user_id"],symbol,curr_price,-shares)

        return redirect("/")
    else:
        options = db.execute("SELECT * FROM users_stocks WHERE user_id = ? ORDER BY shares DESC",
        session["user_id"])
        return render_template("sell.html",options=options)
