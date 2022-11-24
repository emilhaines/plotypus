import ROOT as root
import atlasplots as aplt


def main():
    # Set the ATLAS Style
    aplt.set_atlas_style()

    # Create a figure and axes
    fig, (ax1, ax2) = aplt.ratio_plot(name="fig1", figsize=(800, 800), hspace=0.05)

    # Define "background", "signal" and "data" distributions
    bkg_func = root.TF1("bkg_func", "[0]*exp([1]*x)", 0, 10)
    bkg_func.SetParameters(20, -0.5)

    sig_func = root.TF1("sig_func", "x*gaus(0)", 0, 10)
    sig_func.SetParameters(10, 4, 1)

    # Randomly fill histograms according to the above distributions
    bkg_hist = root.TH1F("bkg_hist", "Background", 50, 0, 10)
    bkg_hist.FillRandom("bkg_func", 10000)
    bkg_hist.SetFillColor(root.kRed+1)
    bkg_hist.SetLineWidth(0)
    bkg_hist.Sumw2()

    sig_hist = root.TH1F("sig_hist", "Signal", 50, 0, 10)
    sig_hist.FillRandom("sig_func", 10000)
    sig_hist.SetFillColor(root.kAzure+1)
    sig_hist.SetLineWidth(0)
    sig_hist.Sumw2()

    data_hist = root.TH1F("data_hist", "Data", 50, 0, 10)
    data_hist.FillRandom("bkg_func", 10000)
    data_hist.FillRandom("sig_func", 10000)
    data_hist.Sumw2()
    data_hist.SetBinErrorOption(root.TH1.EBinErrorOpt.kPoisson)  # Use 68% Poisson errors

    # Stack the background and signal histograms
    bkg_and_sig = root.THStack("bkg_and_sig", "")
    bkg_and_sig.Add(bkg_hist)
    bkg_and_sig.Add(sig_hist)

    # Draw the stacked histogram on these axes
    ax1.plot(bkg_and_sig)

    # Plot the MC stat error as a hatched band
    err_band = aplt.root_helpers.hist_to_graph(
        bkg_and_sig.GetStack().Last(),
        show_bin_width=True
    )
    ax1.plot(err_band, "2", fillcolor=1, fillstyle=3254, linewidth=0)

    # ax1.set_yscale("log")  # uncomment to use log scale for y axis

    # Plot the data as a graph
    data_graph = aplt.root_helpers.hist_to_graph(data_hist)
    ax1.plot(data_graph, "P")

    # Use same x-range in lower axes as upper axes
    ax2.set_xlim(ax1.get_xlim())

    # Draw line at y=1 in ratio panel
    line = root.TLine(ax1.get_xlim()[0], 1, ax1.get_xlim()[1], 1)
    ax2.plot(line)

    # Plot the relative error on the ratio axes
    err_band_ratio = aplt.root_helpers.hist_to_graph(
        bkg_and_sig.GetStack().Last(),
        show_bin_width=True,
        norm=True
    )
    ax2.plot(err_band_ratio, "2", fillcolor=1, fillstyle=3254)

    # Calculate and draw the ratio
    ratio_hist = data_hist.Clone("ratio_hist")
    ratio_hist.Divide(bkg_and_sig.GetStack().Last())
    ratio_graph = aplt.root_helpers.hist_to_graph(ratio_hist)
    ax2.plot(ratio_graph, "P0")

    # Add extra space at top of plot to make room for labels
    ax1.add_margins(top=0.16)

    # Set axis titles
    ax2.set_xlabel("X [GeV]")
    ax1.set_ylabel("Events / 0.2 GeV")
    ax2.set_ylabel("Data / Pred.", loc="centre")

    ax2.set_ylim(0.75, 1.25)
    ax2.draw_arrows_outside_range(ratio_graph)

    # Go back to top axes to add labels
    ax1.cd()

    # Add the ATLAS Label
    aplt.atlas_label(text="Internal", loc="upper left")
    ax1.text(0.2, 0.84, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)

    # Add legend
    legend = ax1.legend(
        loc=(0.68, 0.65, 1 - root.gPad.GetRightMargin() - 0.03, 1 - root.gPad.GetTopMargin() - 0.03),
        textsize=22
    )
    legend.AddEntry(data_graph, "Data", "EP")
    legend.AddEntry(sig_hist, "Signal", "F")
    legend.AddEntry(bkg_hist, "Background", "F")
    legend.AddEntry(err_band, "MC Stat. Unc.", "F")

    # Save the plot as a PDF
    fig.savefig("data_vs_mc.pdf")


if __name__ == '__main__':
    root.gROOT.SetBatch()
    main()