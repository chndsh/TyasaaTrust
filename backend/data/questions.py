# backend/data/questions.py
# TyasaaTrust — Psychometric Question Bank
# 20 scenario questions across 5 thematic clusters
# Each option scores all three traits: integrity, financial_discipline, resilience
# Weights per trait per option: 0 (lowest) to 4 (highest)
#
# Cluster map:
#   C1 — Udharo & Khata (Q01–Q04)
#   C2 — Festive Cycle Pressure (Q05–Q08)
#   C3 — Supplier & Inventory Decisions (Q09–Q12)
#   C4 — Business Setbacks & Loss Recovery (Q13–Q16)
#   C5 — Growth Decisions Under Uncertainty (Q17–Q20)

QUESTION_BANK = [

    # -------------------------------------------------------------------------
    # CLUSTER 1 — Udharo & Khata
    # -------------------------------------------------------------------------

    {
        "id": "Q01",
        "cluster": "C1",
        "scenario": (
            "A loyal customer of three years asks for Udharo of Rs. 12,000 "
            "just before Dashain. He has always repaid — but slowly. Your own "
            "supplier payment is due in ten days and your cash buffer is thin. "
            "What do you do?"
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Extend the full Rs. 12,000. His loyalty over three years "
                    "earns him the benefit of the doubt."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Offer Rs. 6,000 now and explain honestly that your own "
                    "payment is due. Record both halves in your Khata clearly."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Decline entirely this time. You cannot risk your supplier "
                    "relationship over someone else's festive spending."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 4,
                    "resilience": 2
                }
            },
            {
                "id": "D",
                "text": (
                    "Agree verbally but leave it out of the Khata so there is "
                    "no written obligation if things get uncomfortable later."
                ),
                "weights": {
                    "integrity": 0,
                    "financial_discipline": 1,
                    "resilience": 1
                }
            }
        ]
    },

    {
        "id": "Q02",
        "cluster": "C1",
        "scenario": (
            "While reviewing your Khata at month end, you notice a calculation "
            "error in your favour — a regular customer was overcharged Rs. 800 "
            "two weeks ago and has not noticed. The amount would cover your "
            "tea and transport for the week."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Say nothing. The customer did not notice, and the amount "
                    "is small enough that it will not matter to them."
                ),
                "weights": {
                    "integrity": 0,
                    "financial_discipline": 2,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Correct the Khata and inform the customer the next time "
                    "they visit, offering the Rs. 800 as a credit."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Correct the Khata entry privately but wait to see if "
                    "the customer brings it up before saying anything."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            },
            {
                "id": "D",
                "text": (
                    "Call the customer immediately and return the Rs. 800 in "
                    "cash, even if it means going slightly short this week."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 2,
                    "resilience": 4
                }
            }
        ]
    },

    {
        "id": "Q03",
        "cluster": "C1",
        "scenario": (
            "A neighbour shopkeeper asks to borrow your Khata ledger system "
            "style — specifically to see how you structure credit limits per "
            "customer. In the same conversation, he mentions a mutual customer "
            "who owes you Rs. 5,000 also owes him a similar amount."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Share your Khata structure freely and discuss the mutual "
                    "customer openly — the more information shared, the better "
                    "for both businesses."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Share your general Khata structure but decline to discuss "
                    "individual customers. Their debt to you is private."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Share everything including the customer detail — this is "
                    "a practical problem that needs a collective solution."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "D",
                "text": (
                    "Decline to share anything. Your credit system is a "
                    "competitive advantage and not for others to copy."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 3,
                    "resilience": 2
                }
            }
        ]
    },

    {
        "id": "Q04",
        "cluster": "C1",
        "scenario": (
            "A customer disputes an entry in your Khata, claiming they already "
            "paid Rs. 3,500 last month in cash. You have no record of it. They "
            "are angry and threatening to tell others in the bazaar you run a "
            "dishonest shop. You genuinely cannot remember the transaction."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Write off the Rs. 3,500 immediately to avoid any public "
                    "conflict. Protecting your reputation is worth more."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Stand firm. Your Khata shows no payment and you will not "
                    "fabricate a record under social pressure."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Offer to split the difference — write off Rs. 1,750 as a "
                    "goodwill gesture while acknowledging the uncertainty."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 2,
                    "resilience": 3
                }
            },
            {
                "id": "D",
                "text": (
                    "Ask the customer for any receipt or proof and give them "
                    "one week to produce it before making any decision."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            }
        ]
    },

    # -------------------------------------------------------------------------
    # CLUSTER 2 — Festive Cycle Pressure
    # -------------------------------------------------------------------------

    {
        "id": "Q05",
        "cluster": "C2",
        "scenario": (
            "It is six weeks before Tihar. Every year you take a large loan "
            "from a local sahuji to restock for the festive rush. This year "
            "he offers double the usual credit at a higher interest rate. "
            "Sales last Tihar were good but not exceptional."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Accept the full double credit. Festive seasons are the "
                    "best opportunity to grow and you must take it."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Take only what you took last year. You have no data "
                    "justifying the extra risk at a higher rate."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Take a modest increase — maybe 25% more than last year — "
                    "and negotiate the interest rate down before signing."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Decline entirely this year. The higher interest rate "
                    "signals a trap and you will manage with existing stock."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q06",
        "cluster": "C2",
        "scenario": (
            "Dashain sales exceeded your forecast by 40%. You have Rs. 80,000 "
            "in unexpected profit sitting in your cash box. Your family is "
            "pressuring you to renovate the house. Your supplier is offering "
            "a rare bulk discount if you pre-pay before Tihar."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Renovate the house. The family sacrifice during lean "
                    "months deserves to be rewarded when times are good."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Take the supplier discount with all Rs. 80,000. Business "
                    "investment always beats personal spending."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Split the windfall: pre-pay the supplier for the discount, "
                    "set aside a contingency reserve, and give the family a "
                    "smaller but meaningful amount for the house."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Deposit everything into the business account and make no "
                    "immediate decisions. The right use will become clear later."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 3,
                    "resilience": 2
                }
            }
        ]
    },

    {
        "id": "Q07",
        "cluster": "C2",
        "scenario": (
            "Three weeks after Dashain, festive sales have ended and your "
            "shop is noticeably slow. You overstocked on one product category "
            "and Rs. 35,000 worth of goods are sitting unsold. A competitor "
            "across the lane is having a clearance sale at cost price."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Hold your price and wait. Dropping to cost price signals "
                    "desperation and damages your brand for next season."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Match the competitor's clearance price immediately to "
                    "move inventory fast and recover cash flow."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Bundle the slow-moving stock with fast-selling items "
                    "at a modest discount to preserve margin while moving volume."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Donate a portion to a local community event for goodwill "
                    "and sell the rest below cost to close out the season."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 2,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q08",
        "cluster": "C2",
        "scenario": (
            "A friend who runs a clothing stall tells you he makes most of "
            "his annual income in the 45 days around Dashain and Tihar, then "
            "barely breaks even the rest of the year. He asks how you plan "
            "your cash reserves between festive peaks."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "You don't formally plan between peaks — you spend freely "
                    "after a good season and tighten up when things get slow."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 0,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "You keep a fixed percentage of every festive surplus in "
                    "a separate account that is not touched for daily expenses."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "C",
                "text": (
                    "You reinvest everything back into stock immediately after "
                    "the peak so the money is always working."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            },
            {
                "id": "D",
                "text": (
                    "You rely on the sahuji for short-term loans during slow "
                    "months — it has always worked out fine."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            }
        ]
    },

    # -------------------------------------------------------------------------
    # CLUSTER 3 — Supplier & Inventory Decisions
    # -------------------------------------------------------------------------

    {
        "id": "Q09",
        "cluster": "C3",
        "scenario": (
            "Your main supplier offers you a 15% discount if you pay the "
            "full quarterly invoice upfront rather than in monthly instalments. "
            "Paying upfront would exhaust your liquid cash reserve almost "
            "entirely for the next six weeks."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Take the discount without hesitation. 15% is too large "
                    "to leave on the table regardless of cash position."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Decline. Six weeks with no cash buffer is a dangerous "
                    "position — no discount justifies that exposure."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Negotiate: pay 60% upfront for a proportional discount "
                    "and keep the rest as your operating cushion."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Take the discount but immediately take a short-term loan "
                    "from the sahuji to rebuild your cash buffer."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q10",
        "cluster": "C3",
        "scenario": (
            "A new supplier approaches you with products that are 20% cheaper "
            "than your current supplier. However, your current supplier has "
            "extended you generous Udharo terms for two years and helped you "
            "through a difficult flood season last year."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Switch to the new supplier immediately. Business is "
                    "business — price is price."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 3,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Stay with your current supplier entirely. Loyalty during "
                    "hardship cannot be priced at 20%."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            },
            {
                "id": "C",
                "text": (
                    "Show the new quote to your current supplier and give them "
                    "the chance to match or partially match before deciding."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Split your orders between both suppliers to hedge risk "
                    "without fully committing to either."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q11",
        "cluster": "C3",
        "scenario": (
            "Your supplier delivers a batch of goods and leaves before you "
            "complete the count. Later you find five extra units you were not "
            "charged for. The supplier is two hours away by bus and calling "
            "them means admitting the error in your favour."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Keep the extra units and say nothing. Their counting "
                    "error is not your problem to fix."
                ),
                "weights": {
                    "integrity": 0,
                    "financial_discipline": 2,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Call the supplier immediately and arrange to pay for "
                    "the extra five units or return them."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 3
                }
            },
            {
                "id": "C",
                "text": (
                    "Set the extra units aside and mention it casually on "
                    "the next order — no need to make it a special trip."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            },
            {
                "id": "D",
                "text": (
                    "Record the discrepancy in your own ledger and wait for "
                    "the supplier to notice on their end and raise it."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 2,
                    "resilience": 1
                }
            }
        ]
    },

    {
        "id": "Q12",
        "cluster": "C3",
        "scenario": (
            "You discover one of your product lines has a 30% defect rate "
            "from the latest batch. You have already sold some of these to "
            "customers. The supplier is refusing to take responsibility, "
            "claiming the damage happened after delivery."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Accept the supplier's position and absorb the loss "
                    "quietly. Fighting it will damage the relationship."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 2,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Immediately contact affected customers, offer refunds "
                    "or replacements, and pursue the supplier separately "
                    "for compensation."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 4
                }
            },
            {
                "id": "C",
                "text": (
                    "Withdraw the remaining defective stock from sale but "
                    "say nothing to customers who already bought — "
                    "most may not notice."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            },
            {
                "id": "D",
                "text": (
                    "Document everything with photos and receipts, escalate "
                    "to the supplier in writing, and contact customers "
                    "proactively while the evidence is fresh."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            }
        ]
    },

    # -------------------------------------------------------------------------
    # CLUSTER 4 — Business Setbacks & Loss Recovery
    # -------------------------------------------------------------------------

    {
        "id": "Q13",
        "cluster": "C4",
        "scenario": (
            "A flash flood damages your ground-floor storage room. You lose "
            "roughly Rs. 60,000 worth of inventory. You have no insurance. "
            "Your supplier is willing to extend credit. A local NGO is "
            "offering a small grant for flood-affected businesses."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Take the maximum credit from the supplier and apply for "
                    "the NGO grant simultaneously to rebuild as fast as possible."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 3
                }
            },
            {
                "id": "B",
                "text": (
                    "Apply for the NGO grant, take only the minimum credit "
                    "needed to reopen, and scale back product range temporarily "
                    "to reduce risk while rebuilding."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "C",
                "text": (
                    "Close temporarily, assess the full damage, and only "
                    "reopen once you have a clear recovery plan in writing."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            },
            {
                "id": "D",
                "text": (
                    "Sell remaining undamaged stock at a discount immediately "
                    "to generate cash and avoid any new debt during recovery."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 3,
                    "resilience": 4
                }
            }
        ]
    },

    {
        "id": "Q14",
        "cluster": "C4",
        "scenario": (
            "Your most experienced shop assistant quits without notice during "
            "peak season, taking several customer contacts with them to work "
            "for a competitor. Sales drop 25% the following week. "
            "You suspect they shared your pricing structure."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Confront the former employee publicly and warn your "
                    "customers about their conduct."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 1,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Focus entirely on the customers who stayed — call each "
                    "one personally, acknowledge the disruption, and offer "
                    "a small loyalty discount."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 4
                }
            },
            {
                "id": "C",
                "text": (
                    "Immediately revise your pricing and restructure how "
                    "customer information is stored to prevent recurrence."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Accept it as a normal business risk, hire a replacement "
                    "quickly, and move on without making it a larger issue."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q15",
        "cluster": "C4",
        "scenario": (
            "You took a calculated risk on a new product category six months "
            "ago. It has completely failed — zero repeat buyers, and you still "
            "have 80% of the stock unsold. You invested Rs. 45,000. "
            "Your family says you should have listened to their doubts."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Continue selling at full price. Dropping the price now "
                    "means admitting the mistake publicly."
                ),
                "weights": {
                    "integrity": 1,
                    "financial_discipline": 0,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Acknowledge the failure openly, liquidate remaining stock "
                    "at whatever price recovers cash, and document what went "
                    "wrong to avoid repeating it."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "C",
                "text": (
                    "Move the stock to a less visible part of the shop and "
                    "slowly sell it down over a year without drawing attention."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            },
            {
                "id": "D",
                "text": (
                    "Return what you can to the supplier at a loss and write "
                    "off the rest — tying up shelf space on a failed line "
                    "has its own ongoing cost."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q16",
        "cluster": "C4",
        "scenario": (
            "A government road-widening project reduces foot traffic past "
            "your shop by half for an estimated four months. Three of your "
            "neighbouring shopkeepers have already closed temporarily. "
            "Your monthly fixed costs are Rs. 18,000."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Close temporarily like the neighbours and reopen when "
                    "the road work is complete."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 2,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Stay open but immediately cut operating hours to reduce "
                    "costs and redirect energy toward delivery or phone orders."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "C",
                "text": (
                    "Use the slow period to reorganise inventory, repaint "
                    "the shop, and train yourself — invest in the business "
                    "while foot traffic is low anyway."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 3,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Set up a temporary stall at a busier market location "
                    "and run both points simultaneously to compensate."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 3,
                    "resilience": 4
                }
            }
        ]
    },

    # -------------------------------------------------------------------------
    # CLUSTER 5 — Growth Decisions Under Uncertainty
    # -------------------------------------------------------------------------

    {
        "id": "Q17",
        "cluster": "C5",
        "scenario": (
            "A microfinance institution offers you a Rs. 2,00,000 business "
            "loan at 18% annual interest. Your current monthly net profit "
            "averages Rs. 22,000. You have no existing debt. You have two "
            "expansion ideas but have tested neither."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Take the full loan and pursue both expansion ideas "
                    "simultaneously to move fast."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 0,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Decline the loan for now. 18% is too high without "
                    "proof that either idea will work."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 4,
                    "resilience": 2
                }
            },
            {
                "id": "C",
                "text": (
                    "Test one idea using your own savings first. If it "
                    "shows profit within 60 days, then revisit the loan."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Take a smaller loan than offered — just enough to test "
                    "one idea — and negotiate terms before signing."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            }
        ]
    },

    {
        "id": "Q18",
        "cluster": "C5",
        "scenario": (
            "A younger merchant in your area asks you to become a silent "
            "business partner in his new shop. He has energy and ideas but "
            "no track record. He needs Rs. 50,000 from you. "
            "He is your cousin's son."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Invest the full Rs. 50,000. Family trust and belief in "
                    "the next generation matters more than financial caution."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 1,
                    "resilience": 2
                }
            },
            {
                "id": "B",
                "text": (
                    "Decline entirely. Mixing family and money creates problems "
                    "that outlast the business itself."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 3,
                    "resilience": 2
                }
            },
            {
                "id": "C",
                "text": (
                    "Offer a smaller amount you can afford to lose entirely — "
                    "treat it as a gift with upside, not a partnership with "
                    "expectations."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 3
                }
            },
            {
                "id": "D",
                "text": (
                    "Agree to invest but only after seeing a written plan, "
                    "projected costs, and a repayment structure — family "
                    "or not."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            }
        ]
    },

    {
        "id": "Q19",
        "cluster": "C5",
        "scenario": (
            "You have been running your shop for five years and it is stable "
            "but not growing. A business mentor suggests you should raise "
            "your prices by 10–15% — your margins are unusually thin and your "
            "loyal customers may absorb it. You are afraid of losing them."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Keep prices as they are. Loyal customers are built on "
                    "trust and price — raising both risks breaking both."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 1,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Raise prices by the full 15% without announcement. "
                    "If customers ask, explain input costs have risen."
                ),
                "weights": {
                    "integrity": 2,
                    "financial_discipline": 3,
                    "resilience": 2
                }
            },
            {
                "id": "C",
                "text": (
                    "Raise prices gradually over two seasons — 5% now, "
                    "then reassess — and be transparent with regular "
                    "customers about why."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 4,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Raise prices only on new customers while keeping the "
                    "old price for existing loyal customers permanently."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            }
        ]
    },

    {
        "id": "Q20",
        "cluster": "C5",
        "scenario": (
            "Your shop is doing well. A local politician visits and strongly "
            "suggests you donate to his upcoming campaign fund, implying that "
            "your business licence renewal — due in three months — goes "
            "smoother for those who contribute."
        ),
        "options": [
            {
                "id": "A",
                "text": (
                    "Donate a small amount. It is practical to keep local "
                    "officials friendly — this is how things work here."
                ),
                "weights": {
                    "integrity": 0,
                    "financial_discipline": 2,
                    "resilience": 1
                }
            },
            {
                "id": "B",
                "text": (
                    "Donate a large amount. The licence is more valuable than "
                    "the cost of the contribution."
                ),
                "weights": {
                    "integrity": 0,
                    "financial_discipline": 1,
                    "resilience": 1
                }
            },
            {
                "id": "C",
                "text": (
                    "Decline politely and begin documenting the interaction. "
                    "Start preparing your licence renewal paperwork "
                    "thoroughly and ahead of time."
                ),
                "weights": {
                    "integrity": 4,
                    "financial_discipline": 3,
                    "resilience": 4
                }
            },
            {
                "id": "D",
                "text": (
                    "Decline, say nothing to anyone, and hope the licence "
                    "renewal proceeds normally without intervention."
                ),
                "weights": {
                    "integrity": 3,
                    "financial_discipline": 2,
                    "resilience": 2
                }
            }
        ]
    },

]