from flask import Flask, render_template, redirect
#from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
import cloudscraper
import json
from time import sleep

app = Flask(__name__)
#app.config["SQALCHEMY_DATABASE_URI"] = "SQLITE:///database/info.db"
#db = SQLAlchemy(app)

@app.route("/")

def home():
    return render_template("index.html")
 
def manga():
    return render_template("apartamento.html")

@app.route("/readManga/<mangaName>/<int:chapterNumber>/<int:pageNumber>", methods=["GET"])

def readManga(mangaName, chapterNumber, pageNumber):
    naturalPageNumber = pageNumber
    naturalChapterNumber = chapterNumber
    pageNumber -= 1
    chapterNumber -= 1
    chapterImagesURLArray = getIndividualChapterImagesArray(mangaName, naturalChapterNumber)
    chapterImage = chapterImagesURLArray[pageNumber]
    print(pageNumber)

    if(len(chapterImagesURLArray) - 1 == pageNumber):
        chapterImageNext = "/readManga/" + mangaName + "/" + str(naturalChapterNumber + 1) + "/" + str(1)
    else:
        chapterImageNext = "/readManga/" + mangaName + "/" + str(naturalChapterNumber) + "/" + str(naturalPageNumber + 1)

    if(pageNumber != 0):
        chapterImagePrevious = "/readManga/" + mangaName + "/" + str(naturalChapterNumber) + "/" + str(naturalPageNumber - 1)
    elif(pageNumber == 0 and chapterNumber != 0):
        chapterImagePrevious = "/readManga/" + mangaName + "/" + str(naturalChapterNumber - 1) + "/" + str(len(getIndividualChapterImagesArray(mangaName, naturalChapterNumber - 1)))
    elif(pageNumber == 0 and chapterNumber == 0):
        chapterImagePrevious = "/readManga/" + mangaName + "/" + str(naturalChapterNumber) + "/" + str(naturalPageNumber)

    return render_template("reader.html", chapterImage = chapterImage , chapterImageNext = chapterImageNext, chapterImagePrevious = chapterImagePrevious)

@app.route("/descargarManga/<mangaName>/", methods=["GET"])

def descargarManga(mangaName):
    mangaURL = "https://mangahub.io/manga/" + mangaName
    chapterListURLArray = getChapters(mangaURL, mangaName)
    chapterListURLArray = list(reversed(chapterListURLArray))
    resultantList = []
    for element in chapterListURLArray:
        if element not in resultantList:
            resultantList.append(element)
    chapterNumber = len(resultantList)
    #---------------------------------------#
    # Esto retorna las paginas del capitulo #
    #---------------------------------------#
    scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
    photoCode = 0
    entireFuckingManga = []
    for i in range(1, chapterNumber):
        try:
            chapterImagesURLArray = getIndividualChapterImagesArray(mangaName, i)
            print(chapterImagesURLArray)
            entireFuckingManga.append(chapterImagesURLArray)
        except:
            chapterImagesURLArray = getIndividualChapterImagesArray(mangaName, i)
            print(chapterImagesURLArray)
            entireFuckingManga.append(chapterImagesURLArray)
    print(entireFuckingManga)
    print(entireFuckingManga[0][0])
    
    # -------------------------------------------------- #
    # Aqui se hara la descarga de las imagenes del manga #
    # -------------------------------------------------- #

    photoCode = 0

    for i in range(0, len(entireFuckingManga)):
        for j in range(0, len(entireFuckingManga[i])):
                try:
                    img_data = scraper.get(entireFuckingManga[i][j]).content
                    photoCode += 1
                    with open(str(photoCode) + '.jpg', 'wb') as handler:
                        handler.write(img_data)
                except IOError:
                    img_data = scraper.get(entireFuckingManga[i][j]).content
                    photoCode += 1
                    with open(str(photoCode) + '.jpg', 'wb') as handler:
                        handler.write(img_data)

    return render_template("reader.html")

@app.route("/testing/<mangaName>", methods=["GET"])

def testing(mangaName):
    mangaURL = "https://mangahub.io/manga/" + mangaName
    latestChapter = getLatestChapter(mangaURL)
    entireFuckingManga = []
    for i in range(1, latestChapter + 1):
        chapterImages = getChapterImages(mangaName, i)
        print(chapterImages)
        entireFuckingManga.append(chapterImages)
    print(entireFuckingManga[0][0])
    print(entireFuckingManga)
    downloadChapterImages(entireFuckingManga)
    

    

    return "hello world"


def getLatestChapter(mangaURL):
    while(True):
        try:
            scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
            response = scraper.get(mangaURL)
            start = "Chapter <!-- -->"
            end = "</a></span></div><div>"
            latestChapter = int(response.text[response.text.find(start) + len(start):response.text.rfind(end)])
        except:
            continue
        break
    return latestChapter

def getChapterImages(mangaName, chapterID):
    while(True):
        try:
            scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
            response = scraper.post("https://api.mghubcdn.com/graphql", data={"query":"{chapter(x:m01,slug:\"" + mangaName + "\",number:" + str(chapterID) + "){id,title,mangaID,number,slug,date,pages,noAd,manga{id,title,slug,mainSlug,author,isWebtoon,isYaoi,isPorn,isSoftPorn,unauthFile,isLicensed}}}"})
            soup = json.loads(response.text)
        except:
            continue
        chapterImages = []
        for imageCode in (json.loads(soup["data"]["chapter"]["pages"])).values():
            chapterImages.append("https://img.mghubcdn.com/file/imghub/" + imageCode)
        break
    return chapterImages

def downloadChapterImages(entireFuckingManga):
    photoCode = 0
    while(True):
        for i in range(0, len(entireFuckingManga)):
            for j in range(0, len(entireFuckingManga[i])):
                    try:
                        scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
                        img_data = scraper.get(entireFuckingManga[i][j]).content
                        photoCode += 1
                        with open(str(photoCode) + '.jpg', 'wb') as handler:
                            handler.write(img_data)
                    except:
                        continue
        break

def getIndividualChapterImagesArray(mangaName, chapterNumber):
    scraper = cloudscraper.create_scraper(browser='chrome', interpreter='nodejs')
    response = scraper.post("https://api.mghubcdn.com/graphql", data={"query":"{chapter(x:m01,slug:\"" + mangaName + "\",number:" + str(chapterNumber) + "){id,title,mangaID,number,slug,date,pages,noAd,manga{id,title,slug,mainSlug,author,isWebtoon,isYaoi,isPorn,isSoftPorn,unauthFile,isLicensed}}}"})
    print(response.text)
    try:
        soup = json.loads(response.text)
    except:
        getIndividualChapterImagesArray(mangaName, chapterNumber)
    finally:
        soup = json.loads(response.text)
    chapterImagesURLArray = []
    for imageCode in (json.loads(soup["data"]["chapter"]["pages"])).values():
        chapterImagesURLArray.append("https://img.mghubcdn.com/file/imghub/" + imageCode)
    return chapterImagesURLArray

if(__name__ == "__main__"):
    app.run(debug = True, host='0.0.0.0')