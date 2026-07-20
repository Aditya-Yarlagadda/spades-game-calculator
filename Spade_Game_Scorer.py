import gradio as gr
import os
import pandas as pd

DIR = os.path.dirname(os.path.abspath(__file__))
Spades_DIR = os.path.join(DIR, "images/SpadesLogo.png")
XMarkDIR = os.path.join(DIR, "images/xmark.png")
CSS_DIR = os.path.join(DIR, "Spade_Game_Scorer_CSS.css")

with open(CSS_DIR) as f:
    css = f.read()
with gr.Blocks(fill_width=True) as app:
    with gr.Sidebar() as sidebar:
        with gr.Column() as sidebar_column:
            sidebar_markdown = gr.Markdown("""
            # Spades Point Counter
            This program was developed for the popular card game spades. It allows the user to enter the number of people playing
            and keep track of their scores, then it will display a winner screen. 
            """)
            image = gr.Image(value=Spades_DIR, interactive=False, show_label=False, container=False, height=220, buttons=[])
        player_points_view = gr.Markdown(""" """, visible=False)
    with gr.Walkthrough(selected=1) as walkthrough:
        with gr.Step("Game", id=1, interactive=False) as step1:
            with gr.Column(visible=True) as start_section: #startoff for this game
                def check_letters(name, user_list, count):
                    name = name.capitalize()
                    if len(name) > 17:
                        name = name[:17]
                        gr.Warning("Name must be 17 or less characters!")
                        return gr.update(value=name), gr.skip(), gr.skip(), gr.skip(), gr.skip()
                    if len(name) < 2:
                        gr.Warning("Name must be 2 or more characters!")
                        return gr.update(value=None), gr.skip(), gr.skip(), gr.skip(), gr.skip()
                    if name in [row for row in user_list]:
                        gr.Warning("Name already used!")
                        return gr.update(value=None), gr.skip(), gr.skip(), gr.skip(), gr.skip()
                    user_list.append(name)
                    count+=1
                    if count == 2:
                        return (
                            gr.update(label="Enter the name of another person:", value=None),
                            user_list,
                            count,
                            gr.update(value=user_list, row_count = count),
                            gr.update(visible=True)
                            )
                    if count > 12:
                        return (
                            gr.update(label="Maximum number of players reached.", interactive = False, value = None),
                            user_list,
                            count,
                            gr.update(value=user_list, row_count = count),
                            gr.skip()
                            )
                    else:
                        return (
                            gr.update(label="Enter the name of another person:", value=None),
                            user_list,
                            count,
                            gr.update(value=user_list, row_count = count),
                            gr.skip()
                            )
                gr.Markdown("""# Setup""")
                Players = gr.State([])
                Player_Count = gr.State(0)
                Complete_Step = gr.Button(visible=False, value="Complete")
                player_name = gr.Textbox(label="Enter the name of a person playing:", interactive=True)
                Player_View = gr.Dataframe(
                        headers = ["Player Names"],
                        value = [],
                        interactive=False, 
                        scale=1, 
                        static_columns=[0], 
                        wrap=True, 
                        column_count=(1, "fixed"), 
                        buttons=[],
                        type="array"
                        )
                player_name.submit(
                    fn=check_letters,
                    inputs=[player_name, Players, Player_Count], 
                    outputs=[player_name, Players, Player_Count, Player_View, Complete_Step]
                )\
                .then(lambda: gr.update(visible=False), outputs=Player_View)\
                .then(lambda: gr.update(visible=True), outputs=Player_View)
            with gr.Column(visible=False) as game_section:
                column_count = gr.State(0)
                round_count = gr.State(0)
                player_bets = gr.State([])
                player_actual = gr.State([])
                player_points = gr.State({})
                has_run = gr.State(False)
                Bets_Yes = gr.State(True)
                Sidebar_State = gr.State(False)
                history = gr.State([])
                current_label = gr.State("")
                def update_game_table(players, Player_Points):
                        for x in players:
                            Player_Points[x] = 0
                        board = pd.DataFrame([["" for _ in players]], columns=players)
                        board.insert(0, "Round", "")
                        n = len(players)
                        board.at[0, "Round"] = "1"
                        widths = ["8%"]+[f"{92/len(players)}%" for _ in players]
                        start_lbl = f"Enter {players[0]}'s bet:"
                        return (
                            gr.update(value=board, column_widths=widths, static_columns=list(range(n))),
                            gr.update(visible=False),
                            gr.update(visible=True),
                            gr.update(label=start_lbl, value = None),
                            Player_Points,
                            start_lbl,
                            gr.update(visible=False),
                            gr.update(open=False)
                        )
                def take_snapshot(hist, table, col, rnd, bets, actual, hr, by, points, points_view, current_lbl, sidebr): #History Function to Preserve Data for Previous Versions, Run every time the user clicks [ENTER] on the textbox section. 
                    snap = {
                        "table": table.copy() if table is not None else None,
                        "column": col,
                        "round": rnd,
                        "bets": list(bets),
                        "actual": list(actual),
                        "hasrun": hr,
                        "BetsYes": by,
                        "Overall Points": dict(points),
                        "Points View": points_view,
                        "Current Label": current_lbl,
                        "Sidebar": sidebr
                    }
                    return hist + [snap]
                
                def Add_Bet_Win(Input, Players, Table, Bets, Actual, Col_Count, Rnd_Count_, has_run1, Bets_Yes, player_points): #Main Function to Update Game_View Table and Calculate Bets/Actual Points. Returns most values to States to preserve information for take_snapshot()
                    try:
                        Input = int(Input)
                    except (TypeError, ValueError):
                        gr.Warning("Invalid Input")
                        return (gr.skip(),)*14
                    if Input < 0:
                        gr.Warning(f"Cannot input negative numbers!")
                        return (gr.skip(),)*14
                    if isinstance(Input, float) and Input.is_integer():
                        pass
                    elif isinstance(Input, int):
                        pass
                    else:
                        gr.Warning(f"{Input} is an invalid input")
                        return (gr.skip(),)*14

                    if Col_Count < ((len(Players))-1) and Bets_Yes == True:
                        Col_Count +=1
                        Bets.append(Input)
                        Table.at[Rnd_Count_, Players[(Col_Count-1)]] = str(f"{Input}:")
                        current_lbl = f"Enter {Players[Col_Count]}'s bet:"
                        return gr.update(visible=True), Col_Count, gr.update(value=None, label=current_lbl), gr.skip(), gr.update(value = Table), Bets, gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), current_lbl, gr.skip(), gr.skip()
                    else:
                        if not has_run1:
                            Bets.append(Input)
                            Col_Count = 0
                            Table.at[Rnd_Count_, Players[(Col_Count-1)]] = str(f"{Input}:") 
                            current_lbl = f"Enter the amount of sets {Players[Col_Count]} actually obtained."
                            return gr.skip(), Col_Count, gr.update(value = None, label=current_lbl), gr.skip(), gr.update(value=Table), Bets, gr.skip(), True, False, gr.skip(), gr.skip(), current_lbl, gr.skip(), gr.skip()
                        else:
                            if Bets[Col_Count] > Input:
                                    Points = (-1*(Bets[Col_Count]*10)) #If under target multiply their bet by negative 10 and add to score
                            elif Bets[Col_Count] == Input:
                                Points = (Input*10) #On Target Multiply Input by 10 and Add to Score
                            elif Bets[Col_Count] < Input:
                                calc_1 = (Input-Bets[Col_Count])*10 #For every one over target subtract 10, etc winning 1 when betting 0 nets -10.
                                Points = (Bets[Col_Count]*10) - calc_1
                            if Col_Count < (len(Players)-1): #Actual Section until Last Column where points are calculated based on their Bets and their Actual Scores (In this case Input)
                                Col_Count +=1
                                Actual.append(Points)
                                Table.at[Rnd_Count_, Players[Col_Count-1]] = str(f"{Bets[Col_Count-1]}:{Actual[Col_Count-1]}")
                                player_points[Players[Col_Count-1]] = player_points[Players[Col_Count-1]] + Actual[Col_Count-1]
                                sorted_player_points = {}
                                for x in sorted(player_points, key=player_points.get, reverse=True):
                                    sorted_player_points[x] = player_points[x]
                                points_display = """# Player Scoreboard"""
                                for key in sorted_player_points:
                                    points_display = points_display + f"""  \n## <span style='color:#6BAAED'>{key}</span>:    {sorted_player_points[key]}"""
                                current_lbl = f"Enter the amount of sets {Players[Col_Count]} actually obtained."
                                return (
                                    gr.update(visible=True), 
                                    Col_Count, gr.update(value=None, label=current_lbl), 
                                    gr.skip(), gr.update(value=Table), 
                                    gr.skip(), Actual, gr.skip(), 
                                    gr.skip(), sorted_player_points, 
                                    gr.update(value=points_display, visible=True), 
                                    current_lbl, gr.update(open=True), True
                                )
                            else: # Final Actual Section before moving onto next Round, Adds to the Round Count and Resets Column Count to 0.
                                Col_Count +=1
                                Actual.append(Points)
                                Table.at[Rnd_Count_, Players[Col_Count-1]] = str(f"{Bets[Col_Count-1]}:{Actual[Col_Count-1]}")
                                Rnd_Count_ += 1
                                Col_Count = 0
                                Table.at[Rnd_Count_, "Round"] = str(Rnd_Count_+1)
                                player_points[Players[Col_Count-1]] = player_points[Players[Col_Count-1]] + Actual[Col_Count-1]
                                Bets = []
                                Actual = []
                                sorted_player_points = {}
                                for x in sorted(player_points, key=player_points.get, reverse=True):
                                    sorted_player_points[x] = player_points[x]
                                points_display = """# Player Scoreboard"""
                                for key in sorted_player_points:
                                    points_display = points_display + f"""  \n## <span style='color:#6BAAED'>{key}</span>:    {sorted_player_points[key]}"""
                                current_lbl = f"Enter {Players[Col_Count]}'s bet:"
                                return (
                                    gr.skip(), Col_Count, 
                                    gr.update(value=None, label=current_lbl), 
                                    Rnd_Count_, 
                                    gr.update(value=Table), 
                                    Bets, Actual, False, 
                                    True, sorted_player_points, 
                                    gr.update(value=points_display, visible=True), 
                                    current_lbl, gr.update(open=True), True
                                )
                def Undo_Last_Action(history):
                    snap = history[-1]
                    hist = history[:-1]
                    if len(history) == 1:
                        return (
                            hist, 
                            gr.update(value=snap["table"]),
                            snap["column"], snap["round"], 
                            list(snap["bets"]),
                            list(snap["actual"]),
                            snap["hasrun"],
                            snap["BetsYes"],
                            dict(snap["Overall Points"]),
                            gr.update(value = snap["Points View"], visible=False),
                            gr.update(visible=False),
                            gr.update(label=snap["Current Label"]),
                            snap["Current Label"],
                            gr.update(open=snap["Sidebar"])
                        )
                    else:
                        return (
                            hist, 
                            gr.update(value=snap["table"]),
                            snap["column"], snap["round"], 
                            list(snap["bets"]),
                            list(snap["actual"]),
                            snap["hasrun"],
                            snap["BetsYes"],
                            dict(snap["Overall Points"]),
                            gr.update(value = snap["Points View"]),
                            gr.skip(),
                            gr.update(label=snap["Current Label"]),
                            snap["Current Label"],
                            gr.update(open=snap["Sidebar"])
                        )
                explanation = gr.Markdown("""# Game
                            Enter each player bets/actual sets into the system and click [ENTER] to finalize your decision. 
                            After each entry, you can click the X Button to redo that entry. Afterword, you can enter in their actual scores and it will automatically give them their points.""")
                with gr.Row() as data_group:
                    Enter_Bet_Win = gr.Number(label="Enter bet:", interactive=True, scale = 10)
                    Redo_Button = gr.Button(icon=XMarkDIR, value="", visible=False)
                Game_View = gr.Dataframe(
                    interactive=False,
                    buttons=["fullscreen"]
                )
                Enter_Bet_Win.submit(
                    fn=take_snapshot, 
                    inputs = [history, Game_View, column_count, round_count, player_bets, player_actual, has_run, Bets_Yes, player_points, player_points_view, current_label, Sidebar_State], 
                    outputs=[history]
                )\
                .then(
                    fn=Add_Bet_Win, 
                    inputs = [Enter_Bet_Win, Players, Game_View, player_bets, player_actual, column_count, round_count, has_run, Bets_Yes, player_points], 
                    outputs=[Redo_Button, column_count, Enter_Bet_Win, round_count, Game_View, player_bets, player_actual, has_run, Bets_Yes, player_points, player_points_view, current_label, sidebar, Sidebar_State]
                )\
                .then(lambda: gr.update(visible=False), outputs=Game_View)\
                .then(lambda: gr.update(visible=True), outputs=Game_View)
                
                Redo_Button.click(
                    fn=Undo_Last_Action,
                    inputs = [history],
                    outputs = [history, Game_View, column_count, round_count, player_bets, player_actual, has_run, Bets_Yes, player_points, player_points_view, Redo_Button, Enter_Bet_Win, current_label, sidebar],
                    show_progress="hidden"
                    )\
                .then(fn=lambda: gr.update(visible=False), outputs=Game_View, show_progress="hidden")\
                .then(fn=lambda: gr.update(visible=True), outputs=Game_View, show_progress="hidden")

                
            Complete_Step.click(fn=update_game_table, inputs=[Players, player_points], outputs=[Game_View, start_section, game_section, Enter_Bet_Win, player_points, current_label, sidebar_column, sidebar], show_progress="hidden")

        
app.launch(theme=gr.themes.Ocean(), css=css)

