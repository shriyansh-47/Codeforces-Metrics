import streamlit as st
import requests as rq
import datetime as dt
import pandas as pd
import string

st.set_page_config(page_title="CF Metrics", page_icon=":skull:", layout="wide")

st.title("CodeForces Metrics 📊")

def input_username():
    username = st.sidebar.text_input("Enter your C.F. Username")
    if st.sidebar.button("Submit"):
        if username:
            data = fetch_data(username)
            if data != None:
                display(*data) #Unpacking the tuple received from fetch_data()
        else:
            st.sidebar.error("Atleast type something man")

@st.cache_data(ttl=300) #Caching the returned value of fetch_data(), the value remains in cache for 300sec, reduces the number of API req.
def fetch_data(username):
    info_url = "https://codeforces.com/api/user.info"
    rating_url = "https://codeforces.com/api/user.rating"
    submission_url = "https://codeforces.com/api/user.status"

    info_data = rq.get(info_url, params={"handles":username,"checkHistoricHandles":"false"}).json()

    if info_data["status"] != "OK":
        st.error("Enter a valid username")
        return None
    
    rating_data = rq.get(rating_url, params={"handle":username}).json()
    submission_data = rq.get(submission_url,params={"handle":username, "from":1}).json()

    return (info_process(info_data), rating_process(rating_data), submission_process(submission_data))

def info_process(info):
    user = info["result"][0]
    user_data = {
        "handle": user.get("handle"),
        "rating": user.get("rating"),
        "friends": user.get("friendOfCount"),
        "tier": user.get("rank"),
        "maxRating": user.get("maxRating"),
        "maxTier": user.get("maxRank"),
        "regDate": user.get("registrationTimeSeconds"),
        "pfp": user.get("titlePhoto"),
        "country": user.get("country", "_"),
        "org": user.get("organization", "_"),
        "fname": user.get("firstName", "_"),
        "lname": user.get("lastName", "_"),
        "email": user.get("email", "_")
    }

    return user_data
    
def date_formatter(date):
    dt_obj = dt.datetime.fromtimestamp(date)
    return dt_obj.strftime("%b %d, %Y")

def rating_process(data):
        contests = data["result"]
        rating={
            "cCount" : len(contests),
            "pdelta" : 0,
            "ndelta" : 0,
            "rate" : [{"date": 0, "newRating":0}],
            "bestContest":{"rank":1000000,"cName":"_","cId":0},
            "bestDelta" : {"delta":0,"cName":"_","cId":0}
        }

        cnt=0
        for dict in contests:

            if dict["rank"] < rating["bestContest"]["rank"]:
                rating["bestContest"]["rank"]=dict["rank"]
                rating["bestContest"]["cName"]=dict["contestName"]
                rating["bestContest"]["cId"]=dict["contestId"]

            rating["rate"].append({"date": dict["ratingUpdateTimeSeconds"], "newRating": dict["newRating"]})

            diff = dict["newRating"]-dict["oldRating"]
            cnt+=1

            if diff >= 0:
                rating["pdelta"]+=1
            else:
                rating["ndelta"]+=1

            if cnt <= 3:
                continue

            if diff > rating["bestDelta"]["delta"]:
                rating["bestDelta"]["delta"]=diff
                rating["bestDelta"]["cName"]=dict["contestName"]
                rating["bestDelta"]["cId"]=dict["contestId"]

        if rating["bestContest"]["rank"] == 1000000:
            rating["bestContest"]["rank"] = 0

        return rating

def submission_process(submission):
    data = submission["result"]
    sub = {"recent_solve":None,
           "first_solve":None,
           "solved":set(),
           #"rating":{"800":0,"900":0,"1000":0,"1100":0,"1200":0,"1300":0,"1400":0,"1500":0,"1600":0,"1700":0,"1800":0,"1900":0,"2000":0},
           "index" : [{"alpha": char, "val": 0} for char in string.ascii_uppercase], # Read more
           "skipped":set()
           }
    
    #print(data)
    cnt = 0
    for dict in data:
        # cnt+=1
        # print(cnt, end = "  ")
        # print(dict)

        verdict = dict.get("verdict" , None)
        probId = dict.get("problem").get("contestId","_")
        probIndex = dict.get("problem").get("index","_")
        probUID = str(probId) + probIndex
        probName = dict.get("problem").get("name","_")
        probRate = dict.get("problem").get("rating",None)

        if verdict == "SKIPPED":
            cnt+=1
        if verdict == "SKIPPED" and probUID not in sub["solved"]:
            sub["skipped"].add(probUID)

        if verdict == "OK":
            
            if probUID not in sub["solved"] and probIndex != "_":
                sub["index"][ord(probIndex[0])-65]["val"]+=1
 
            #no need of the line below since the given json is in reverse order,
            #therefore we'd know beforehand if we have solved the given problem,
            #after it was skipped
            #sub["skipped"].discard(probUID) #Removes the Solution that got accepted after skipping
            sub["solved"].add(probUID)
            sub["first_solve"] = probUID + " " + probName

            if len(sub["solved"]) == 1:
                sub["recent_solve"] = probUID + " " + probName
    return sub


# def dict_formatter(dict):
#     return {k:v for k,v in dict.items() if v != 0}

def display(user,rating,sub):

    c1,c2=st.columns([3,1])
    with c1:
        rating["rate"][0]["date"] = user['regDate']

        #Rating Graph:-
        #Read more about this(Plotting, Autosorting of Stirngs by Streamlit, more)
        st.subheader("Rating progress over time")
        dataframe = pd.DataFrame(rating["rate"])
        dataframe["date"] = pd.to_datetime(dataframe["date"], unit="s")
        #dataframe has 2 colums ["date"] & ["newRating"], the above line converts(vectorized operation) the unix timestamp code into Pandas Datetime Object
        # 1704067200 -> 2024-01-01 00:00:00
        # Unit tells what kind of unix timestamp is give, millisecond(ms) or second(s)

        # chart = (alt.Chart(dataframe).mark_line().encode(x=alt.X("date:T", title="Date", sort=None), y=alt.Y("newRating:Q", title="Rating"), tooltip=["date:T" , "newRating:Q"]))
        # st.altair_chart(chart,use_container_width=True)

        st.line_chart(dataframe,x="date",y="newRating",x_label="Timeline",y_label="Rating")
    with c2:
        st.image(user["pfp"])
    
    with st.expander("Personal Details"):
        col1,col2 = st.columns(2)
        with col1:
            st.write("Name : ")
            st.write("Handle : ")
            st.write("Country : ")
            st.write("Organization : ")
            st.write("Number of Friends : ")
            st.write("E-mail : ")
            st.write("Registered On : ")
        with col2:
            #Note the usage of '' inside dictionaries when used with f""
            st.write(f"{user['fname']} \t {user['lname']}")
            st.write(f"{user['handle']}")
            st.write(f"{user['country']}")
            st.write(f"{user['org']}")
            st.write(f"{user['friends']}")
            st.write(f"{user['email']}")
            st.write(f"{date_formatter(user['regDate'])}")


    with st.expander("Coding Profile"):
        col1,col2 = st.columns(2)
        with col1:
            #Delta Graph:-
            st.subheader("+ve Delta vs -ve Delta")

            delta = [{"delta_type":"+ve","delta_val":rating["pdelta"]},
                     {"delta_type":"-ve","delta_val":rating["ndelta"]}]
            
            df = pd.DataFrame(delta)
            st.bar_chart(df,x="delta_type", y="delta_val", x_label="", y_label="")
            
            st.write("Rating : ")
            st.write("Rank : ")
            st.write("Total Contests Given : ")
            st.write("Total Problems Solved : ")
            st.write("Number of Skipped Problems : ")
            st.write("First Solve : ")
            st.write("Most Recent Solve : ")
            st.write("Best Contest : ")
            st.write("Best Delta in a Contest : ")

        with col2:
            #ABCs graph:-
            st.subheader("Index wise problem solved")
            df = pd.DataFrame(sub["index"])
            st.bar_chart(df, x="alpha", y="val", x_label="", y_label="")

            st.write(f"***{user['rating']}*** (Max :- *{user['maxRating']}*)")
            st.write(f"***{user['tier']}*** (Max :- *{user['maxTier']}*)")
            st.write(f"***{rating['cCount']}***")
            st.write(f"***{len(sub['solved'])}***")
            st.write(f"***{len(sub['skipped'])}***")
            st.write(sub["first_solve"])
            st.write(sub["recent_solve"])
            st.write(f"***{rating['bestContest']['rank']}*** in ***{rating['bestContest']['cName']}*** (ID :- {rating['bestContest']['cId']})")
            st.write(f"***{rating['bestDelta']['delta']}*** in ***{rating['bestDelta']['cName']}*** (ID :- {rating['bestDelta']['cId']})")
        

        if len(sub["skipped"]) != 0:
            st.error(f"You got ***{len(sub["skipped"])}*** Skipped problems ")
            c1,c2,c3,c4,c5=st.columns(5)
            with c3:
                st.image("https://media.tenor.com/He4G89iTWzIAAAAe/doggggg.png",
                         width=200)
        else:
            st.success("NO SKIPPED PROBLEMS")
            c1,c2,c3,c4,c5=st.columns(5)
            with c3:
                st.image("https://media.tenor.com/HUz1LwDn_lAAAAAM/smile.gif",
                         width=200)



def main():
    #print("Hello from codeforces-dashboard!")
    input_username()


if __name__ == "__main__":
    main()
