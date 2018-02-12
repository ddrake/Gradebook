import numpy as np
from matplotlib import pyplot as plt 

def plot_hist(pcts, title):
    h=np.histogram(pcts,bins=(0,60,70,80,90,200))
    barlist = plt.bar(range(5),h[0],width=0.85)
    colors = ['#ff0000', '#ff8000', '#ffff00', '#0080ff','#00ff00']
    for i in range(5):
        barlist[i].set_color(colors[i])
    xlab=['F', 'D', 'C', 'B', 'A']
    plt.xticks(np.arange(5),xlab)
    plt.title(title)
    plt.show()

class SimpleReport:
    """ A pretty flexible and simple report class """
    def __init__(self, title, name_col_width=16, data_col_width=6, total_col_width=8, \
            name_col_name='Name', row_headings=[], col_headings=[], data=[], \
            total_col=None, total_col_name="Total", pct_col=None, has_average_row=False):
        self.title = title
        self.name_col_width = name_col_width
        self.data_col_width = data_col_width
        self.total_col_width = total_col_width
        self.name_col_name = name_col_name
        self.row_headings = row_headings
        self.col_headings = col_headings
        self.data = data
        self.total_col = total_col
        self.total_col_name = total_col_name
        self.pct_col = pct_col
        self.has_average_row = has_average_row

    def render(self):
        out = self.render_header()
        out += self.render_body()
        out += self.render_footer()
        return out

    def render_header(self):
        n,m = self.data.shape
        out = self.title + "\n"
        out += "-"*len(self.title) + "\n"
        out += self.name_col_name.ljust(self.name_col_width)
        out += "".join([h.rjust(self.data_col_width) for h in self.col_headings])
        if self.total_col is not None: out += self.total_col_name.rjust(self.total_col_width)
        if self.pct_col is not None: out += "Pct.".rjust(self.total_col_width)
        out += "\n" + self.hrule(m)
        return out
 
    def render_body(self):
        out = ""
        n,m = self.data.shape
        for i in range(n):
            out += "{}".format(self.row_headings[i]).ljust(self.name_col_width)
            for j in range(m):
                out += "{0:.1f}".format(self.data[i,j]).rjust(self.data_col_width)
            if self.total_col is not None: 
                out += "{0:.1f}".format(self.total_col[i]).rjust(self.total_col_width)
            if self.pct_col is not None: 
                out += "{0:.1f}".format(self.pct_col[i]).rjust(self.total_col_width)
            out += "\n"
        return out
 
    def render_footer(self):
        n,m = self.data.shape
        out = self.hrule(m)
        if self.has_average_row:
            out += "Average".ljust(self.name_col_width)
            for j in range(m):
                out += "{0:.1f}".format(self.data[:,j].mean()).rjust(self.data_col_width)
            if self.total_col is not None: 
                out += "{0:.1f}".format(self.total_col.mean()).rjust(self.total_col_width)
            if self.pct_col is not None: 
                out += "{0:.1f}".format(self.pct_col.mean()).rjust(self.total_col_width)
        out += "\n\n"
        return out

    def hrule(self, m):
        out = "-" * (self.name_col_width + m * self.data_col_width)
        if self.total_col is not None: out += "-" * self.total_col_width
        if self.pct_col is not None: out += "-" * self.total_col_width
        return out + "\n"


