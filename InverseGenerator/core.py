def createNotes(lane, offset, notetype=None, endnote=None):
    # 1 3 5 7
    # lane,0,offset,5,0,1:0:0:0:
    lanecode = 64 * (2 * lane + 1)
    if notetype == None:
        return "%d,0,%d,1,0,0:0:0:0:\n" % (lanecode, offset)
    if notetype == "LN":
        if endnote == None or endnote < offset:
            return createNotes(lane, offset)
        return "%d,0,%d,128,0,%d:0:0:0:0:\n" % (lanecode, offset, endnote)

def to_inverse(osufile, start, stop, denseness, bpm, write=True):
    if isinstance(osufile, str):
        f = open(osufile, "r").readlines()
    else:
        f = osufile
    if write:
        newosufile = open("{}\\Inverse.osu".format("\\".join(osufile.split("\\")[:len(osufile.split("\\") - 1)])), "w+")
    inverseratio = 1000 / (bpm * denseness / 60)
    newnotes = []
    c = 0
    for i in range(len(f)):
        check = 0
        try:
            if "HitObjects" in f[i]:
                c = 1
            if int(f[i].split(",")[2]) >= start and c == 1 and int(f[i].split(",")[2]) <= stop:
                check = 1
        except:
            pass
        if f[i].split(",")[-1] != "0:0:0:0:\n" or check == 0:
            newnotes.append(f[i])
            continue
        note = ((int(f[i].split(",")[0]) // 64) - 1) // 2
        offset = int(f[i].split(",")[2])
        lnoffset = 0
        for n in range(i, len(f), 1):
            if offset < int(f[n].split(",")[2]) and int(f[n].split(",")[0]) == int(f[i].split(",")[0]):
                lnoffset = int(f[n].split(",")[2]) - inverseratio
                break
        newnotes.append(createNotes(note, offset, notetype="LN", endnote=lnoffset))
    if write:
        for i in newnotes:
            newosufile.write(i)
    else:
        return newnotes

def findmainbpm(file):
    osufile = open(file, 'r')
    timing = osufile.readlines()
    main_bpm = -1; newbpmoffset = 0; bpmandoffset = []
    chk = 0; oldbpm = 1
    chk3 = 0; first_bpm = 1
    #mainbpmfinding
    for tp in timing:
        if("[TimingPoints]" in tp):
            chk = 1
        if("[HitObjects]" in tp):
            chk = 0
        if(chk == 1 and "[TimingPoints]" not in tp and tp != "\n"):
            x = tp.split(",")
            if(chk3 == 0):
                timing_num = float(x[1])
                first_bpm = 60000 / timing_num
                chk3 = 1
            x = tp.split(",")
            isBPM = int(x[6])
            timing_num = float(x[1])
            os = float(x[0])
            if(isBPM == 1):
                bao = {}
                newbpm = 60000 / timing_num
                bao['bpm'] = oldbpm
                bao['offset'] = os - newbpmoffset
                chk2 = 0
                for i in bpmandoffset:
                    if i['bpm'] == bao['bpm']:
                        i['offset'] += bao['offset']
                        chk2 = 1
                if chk2 == 0:
                    bpmandoffset.append(bao)
                newbpmoffset = os
                oldbpm = newbpm
    last_bpm = oldbpm
    lastbpmoffset = newbpmoffset
    index = -1
    while timing[index] == "\n":
        index -= 1
    lasbpmo = int(timing[index].split(",")[2]) - lastbpmoffset
    last = {}
    last['bpm'] = last_bpm
    last['offset'] = lasbpmo
    bpmandoffset.append(last)
    maxsumoffset = 0
    for i in bpmandoffset:
        if(i['offset'] > maxsumoffset):
            main_bpm = i['bpm']
            maxsumoffset = i['offset']
    if(main_bpm == 1):
        main_bpm = first_bpm
    osufile.close()
    ###################################################################
    return main_bpm

class applyToFile:
    def __init__(self, osufile):
        with open(osufile, "r") as f:
            f = f.readlines()
            try:
                bookmarks = f[f.index("[Editor]\n") + 1][len("Bookmarks: "):]
                bookmarks = bookmarks[:len(bookmarks) - 1]
                bookmarks = [int(i) for i in bookmarks.split(",")]
            except:
                bookmarks = [0]
            if len(bookmarks) % 2 == 1:
                # add the last note position
                bookmarks.append(int(f[-2].split(",")[2]))
            marks = [[bookmarks[i], bookmarks[i+1]] for i in range(0, len(bookmarks), 2)]
            bookmarks = marks
        self.bookmarks = bookmarks
        self.file = f
        self.directory = "/".join(osufile.split("/")[:len(osufile.split("/")) - 1])
        self.mainbpm = findmainbpm(osufile)
    
    def writefile(self, newdifficulty):
        with open(self.directory + "/new.osu", "w+") as new:
            for i in self.file:
                if "Version:" in i:
                    new.write("Version:{}\n".format(newdifficulty))
                    continue
                if "BeatmapID:" in i:
                    new.write("BeatmapID:0\n")
                    continue
                new.write(i)

    def inverse(self, gap: list):
        if len(gap) < len(self.bookmarks):
            self.bookmarks = self.bookmarks[:len(gap)]
        elif len(gap) > len(self.bookmarks):
            gap = gap[:len(self.bookmarks)]
        for i in range(len(gap)):
            start = self.bookmarks[i][0]
            end = self.bookmarks[i][1]
            denseness = gap[i]
            self.file = to_inverse(self.file, start, end, denseness, self.mainbpm, write=False)