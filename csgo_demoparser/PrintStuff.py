def print_header(file, header):
    file.write("\nDEMO HEADER:\n")
    file.write("    header= {}\n".format(header.header))
    file.write("    protocol= {}\n".format(header.demo_protocol))
    file.write("    net_proto= {}\n".format(header.network_protocol))
    file.write("    server_name= {}\n".format(header.server_name))
    file.write("    client_name= {}\n".format(header.client_name))
    file.write("    map_name= {}\n".format(header.map_name))
    file.write("    game_dir= {}\n".format(header.game_directory))
    file.write("    play_time= {}\n".format(header.playback_time))
    file.write("    ticks= {}\n".format(header.ticks))
    file.write("    frames= {}\n".format(header.frames))
    file.write("    signon= {}\n".format(header.signon_length))


def print_event_list(file, my_list):
    file.write("\nGAME EVENTS LIST:")
    for item in my_list.items():
        file.write("\n  > {}, {} <\n    ....".format(item[0], item[1].name))
        for item2 in item[1].keys:
            file.write(" {} /".format(item2.name))
    file.write("\n")


def print_counter(file, table):
    file.write("\nCOMMANDS:\n")
    for item in sorted(table[0]):
        file.write("    cmd= {} / count= {}\n".format(item[0], item[1]))
    file.write("MESSAGES:\n")
    for item in sorted(table[1]):
        file.write("    msg= {} / count= {}\n".format(item[0], item[1]))
    file.write("EVENTS:\n")
    for item in sorted(table[2]):
        file.write("    ev= {} / count= {}\n".format(item[0], item[1]))


def print_userinfo(file, data):
    for x in data:
        if x.name == "userinfo":
            data = x.data
            break
    file.write("\nUSERINFO FROM TABLE:\n")
    file.write("    version / xuid / name / uid / guid / fid / fname / fakepl / isHLTV / custom / files / eid / tbd\n")
    for item in data:
        x = item["user_data"]
        if x:
            file.write("{}:   {} / {} / {} / {} / ".format(item["entry"], x.version, x.xuid, x.name, x.user_id))
            file.write("{} / {} / {} / {} / ".format(x.guid, x.friends_id, x.friends_name, x.fake_player))
            file.write("{} / {} / {} / ".format(x.is_hltv, x.custom_files, x.files_downloaded))
            file.write("{} / {} ///\n".format(x.entity_id, x.tbd))


def print_players_userinfo(file, data):
    file.write("\nUSERINFO:\n")
    file.write("    version / xuid / name / uid / guid / fid / fname / fakepl / isHLTV / custom / files / eid / tbd\n")
    for p in data.items():
        x = p[1]
        if x:
            file.write("{}:   {} / {} / {} / {} / ".format(p[0], x.version, x.xuid, x.name, x.user_id))
            file.write("{} / {} / {} / {} / ".format(x.guid, x.friends_id, x.friends_name, x.fake_player))
            file.write("{} / {} / {} / ".format(x.is_hltv, x.custom_files, x.files_downloaded))
            file.write("{} / {} ///\n".format(x.entity_id, x.tbd))


def print_match_stats(file, data):
    file.write("\nMATCH STATS:\n")
    for x in data.items():
        if x[0] == "otherdata":
            continue
        file.write("\nRound {}:\n".format(x[0]))
        file.write("team2= {} / team3= {}\n\n".format(x[1].score_team2, x[1].score_team3))
        file.write("        K / A / D\n")
        for i in range(len(x[1].pscore)):
            file.write("{} > {} / {} / {}, team= {} xuid= {}\n".format(x[1].pscore[i].player.name, x[1].pscore[i].k,
                                                                       x[1].pscore[i].a, x[1].pscore[i].d,
                                                                       x[1].pscore[i].player.start_team,
                                                                       x[1].pscore[i].player.userinfo.xuid))
        file.write("...............................................................\n")


def print_entities(file, data):
    file.write("\nENTITIES:\n")
    for x in data.items():
        if x[1] is None or x[1].parse is False:
            continue
        file.write("\n\nENTITY #{}: {} //".format(x[0], x[1].class_name))
        for x2 in x[1].props.items():
            file.write("\n....{} //\n........".format(x2[0]))
            for x3 in x2[1].items():
                file.write("{} = {} // ".format(x3[0], x3[1]))
    file.write("\n")
