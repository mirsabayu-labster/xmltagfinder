import sublime
import sublime_plugin
import xml.etree.ElementTree as ET


class tagClass:

    def __init__(self):
        self.tag = ""
        self.attributes = {}


class QueryData:

    def __init__(self):
        self.tagId = ""
        self.attributesId = ""
        self.pointerString = ""
        self.list_of_element = []
        self.window = None
        self.getViewFlag = 0

    def getView(self):
        view = self.window.active_view()
        viewed_region = sublime.Region(0, view.size())
        region_string = view.substr(viewed_region)
        self.collectData(region_string, view)

    def collectData(self, txt, view):
        self.list_of_element.clear()
        root = ET.fromstring(txt)
        if(len(root) <= 0):
            return
        if(self.getViewFlag == 0):
            self.collectRootChildData(root, view)
        elif(self.getViewFlag == 1):
            self.collectAttributesData(root, view)
        elif(self.getViewFlag == 2):
            self.collectAttributesValueData(root, view)

    def collectRootChildData(self, root, view):
        if(len(root) > 0):
            for child in root:
                self.collectRootChildData(child, view)
                if(child.tag not in self.list_of_element):
                    self.list_of_element.append(child.tag)
        else:
            if(root.tag not in self.list_of_element):
                self.list_of_element.append(root.tag)

    def collectAttributesData(self, root, view):
        for element in root.iter(self.tagId):
            for att in element.attrib:
                if (att != None and att not in self.list_of_element):
                    self.list_of_element.append(att)

    def collectAttributesValueData(self, root, view):
        for element in root.iter(self.tagId):
            if(element.attrib.get(self.attributesId, "") not in self.list_of_element):
                self.list_of_element.append(
                    element.attrib.get(self.attributesId, ""))

    def showPointedLocation(self):
        view = self.window.active_view()
        reg_element = view.find(
            " " + self.attributesId + "=" + '"' + self.pointerString + '"', 0, sublime.LITERAL)
        line_region = view.line(reg_element)
        highlight = view.get_regions("bookmarks")
        highlight.append(line_region)
        view.add_regions("bookmarks", highlight, "string",
                         "dot", sublime.PERSISTENT)
        view.show(line_region)
        view.sel().clear()
        view.sel().add(line_region)

    def eraseLine(self):
        view = self.window.active_view()

    def getCollectedData(self):
        return self.list_of_element

query_data = QueryData()


def print_done_tag(args):
    query_data.tagId = query_data.getCollectedData()[args]
    query_data.window.run_command("labster_attributes")


def print_done_attributes(args):
    print(query_data.getCollectedData()[args])
    query_data.attributesId = query_data.getCollectedData()[args]
    query_data.window.run_command("labster_attributes_value")


def print_done_attributes_value(args):
    print("attributes_value :: " + query_data.getCollectedData()[args])
    query_data.pointerString = query_data.getCollectedData()[args]
    query_data.showPointedLocation()


def print_highlight_attributes_value(args):
    query_data.pointerString = query_data.getCollectedData()[args]
    query_data.showPointedLocation()


class LabsterTagCommand(sublime_plugin.WindowCommand):

    def run(self):
        if(len(query_data.getCollectedData()) > 0):
            self.window.show_quick_panel(query_data.getCollectedData(
            ), print_done_tag, sublime.MONOSPACE_FONT, 0, None)


class LabsterAttributesCommand(sublime_plugin.WindowCommand):

    def run(self):
        print("attributes")
        if(len(query_data.getCollectedData()) > 0):
            self.window.show_quick_panel(query_data.getCollectedData(
            ), print_done_attributes, sublime.MONOSPACE_FONT, 0, None)


class LabsterAttributesValueCommand(sublime_plugin.WindowCommand):

    def run(self):
        print("attibutes_value")
        if(len(query_data.getCollectedData()) > 0):
            self.window.show_quick_panel(query_data.getCollectedData(
            ), print_done_attributes_value, sublime.MONOSPACE_FONT, 0, print_highlight_attributes_value)


class LabsterEraseCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.view.erase_regions("bookmarks")


class LabsterEventListener(sublime_plugin.EventListener):

    def on_window_command(self, window, command_name, args):

        if(command_name == "labster_tag"):
            query_data.getViewFlag = 0
        elif(command_name == "labster_attributes"):
            query_data.getViewFlag = 1
        elif(command_name == "labster_attributes_value"):
            query_data.getViewFlag = 2
        query_data.window = window
        query_data.getView()

# LABSTER XML BREAKER


class LabsterExpandTextCommand(sublime_plugin.TextCommand):

    def processView(self, edit):
        selection = self.view.sel()
        selectionText = self.view.substr(selection[0])
        caret = self.view.substr(sublime.Region(
            selection[0].end() - 2, selection[0].end()))
        if(caret != "/>"):
            selectionText = selectionText.replace(">", "/>")
            self.flag = 1
        self.processTree(selection[0], selectionText, edit)

    def processTree(self, region, string, edit):
        root = ET.fromstring(string)

        returnedString = "<" + root.tag + "\n"
        for att in root.attrib:
            if(att == "Id"):
                returnedString += att + "=" + '"' + \
                    root.attrib.get(att, "") + '"\n'
        for att in root.attrib:
            if(att != "Id"):
                returnedString += att + "=" + '"' + \
                    root.attrib.get(att, "") + '"\n'
        caret = self.view.substr(sublime.Region(
            region.end() - 2, region.end()))
        if(self.flag == 0):
            returnedString += '/>'
        else:
            returnedString += '>'
        self.view.replace(edit, region, returnedString)

    def run(self, edit):
        self.flag = 0
        self.processView(edit)


class LabsterCompressTextCommand(sublime_plugin.TextCommand):

    def processView(self, edit):
        selection = self.view.sel()
        selectionText = self.view.substr(selection[0])
        caret = self.view.substr(sublime.Region(
            selection[0].end() - 2, selection[0].end()))
        if(caret != "/>"):
            selectionText = selectionText.replace(">", "/>")
            self.flag = 1
        self.processTree(selection[0], selectionText, edit)

    def processTree(self, region, string, edit):
        root = ET.fromstring(string)

        returnedString = "<" + root.tag + " "
        for att in root.attrib:
            if(att == "Id"):
                returnedString += att + "=" + '"' + \
                    root.attrib.get(att, "") + '" '
        for att in root.attrib:
            if(att != "Id"):
                returnedString += att + "=" + '"' + \
                    root.attrib.get(att, "") + '" '
        caret = self.view.substr(sublime.Region(
            region.end() - 2, region.end()))
        if(self.flag == 0):
            returnedString += '/>'
        else:
            returnedString += '>'
        self.view.replace(edit, region, returnedString)

    def run(self, edit):
        self.flag = 0
        self.processView(edit)


class QuizExtractorQueryData:

    def __init__(self):
        self.tags = ""
        self.attributes = ""

    def getView(self, view):
        viewed_region = sublime.Region(0, view.size())
        region_string = view.substr(viewed_region)
        self.collectData(region_string, view)

    def collectData(self, txt, view):
        root = ET.fromstring(txt)
        if(len(root) <= 0):
            return
        self.collectCorrectAnswer(root, view)

    def collectCorrectAnswer(self, root, view):
        if(len(root) > 0):
            print("vxcvxvxvxc")
            count = 0
            for element in root.iter("Option"):
                if(element.attrib.get("IsCorrectAnswer", "") != ""):
                    count += 1
                    print("{}:: ".format(count) + element.attrib["Sentence"])

quizExtractor = QuizExtractorQueryData()


class LabsterQuizAnswerExtractorCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        print("kampret")
        quizExtractor.getView(self.view)
