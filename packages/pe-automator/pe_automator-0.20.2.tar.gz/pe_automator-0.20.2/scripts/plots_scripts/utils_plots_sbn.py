import bilby 
import matplotlib.pyplot as plt 

import numpy as np  
import json
import os, math, re
import seaborn as sns 
import matplotlib.gridspec as gridspec 
import corner

import scipy
from scipy.stats import gaussian_kde

alkde  = 0.00
alhist = 0.75
histlw = 1.75
labfs  = 22

key_labels = {'mass_ratio': '$1/q$'
              , 'chirp_mass': r'$\mathcal{M}[M_{\odot}]$'
              , 'total_mass': r'$M_T[M_{\odot}]$'
              , 'mass_1': r'$m_1[M_{\odot}]$'
              , 'mass_2': r'$m_2[M_{\odot}]$'
              , 'mass_1_source': r'$m_1^{src}[M_{\odot}]$'
              , 'mass_2_source': r'$m_2^{src}[M_{\odot}]$'
              , 'total_mass_source':r'$M_T^{src}[M_{\odot}]$'
              , 'chi_eff': r'$\chi_\mathrm{eff}$'
              , 'chi_p': r'$\chi_\mathrm{p}$'
              , 'luminosity_distance': r'$d_L$[Mpc]'
              , 'dec': r'$\delta[rad]$'
              , 'ra': r'$\alpha[rad]$'
              , 'theta_jn': r'$\theta_\mathrm{JN}$[rad]'
              , 'a1':r'$a_1$'
              , 'a2':r'$a_2$'
              , 'a_1':r'$a_1$'
              , 'a_2':r'$a_2$'
              , 'geocent_time':r'$t_c$[s]'
              , 'tilt_1':r'$t_1$'
              , 'tilt_2':r'$t_2$'
              , 'chi_1':r'$\chi_1$'
              , 'chi_2':r'$\chi_2$'
              , 'eccentricity':r'$e_0$'
              , 'mean_anomaly':r'$\zeta_0$'
              ,'mean_per_ano':r'$\zeta_0$'
              , 'e_gw':r'$e_{\mathrm{gw}}$'
              , 'l_gw':r'$l_{\mathrm{gw}}$'
              ,'log_likelihood':'log_likelihood'
		,'final_spin_TPHM':r'$a_f$'
              }
sns.set_palette("deep")


# Remove some annoying panda warnings when plotting the posteriors
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Matplotlib settings
import seaborn as sns
sns.set_palette("colorblind")
#sns.set(style="white",font_scale=2.)

golden = 1.6180339887498948482045868 
plt.rc('text', usetex=True) # Comment this out if you don't have LaTeX in your PATH!

#plt.style.use('test.mplstyle')

alkde  = 0.00
alhist = 0.75
histlw = 1.75
labfs  = 22

"""
key_labels = {'mass_ratio': '$1/q$'
              , 'chirp_mass': r'$\mathcal{M}[M_{\odot}]$'
              , 'total_mass': r'$M_T[M_{\odot}]$'
              , 'mass_1': r'$m_1[M_{\odot}]$'
              , 'mass_2': r'$m_2[M_{\odot}]$'
              , 'mass_1_source': r'$m_1^{src}[M_{\odot}]$'
              , 'mass_2_source': r'$m_2^{src}[M_{\odot}]$'
              , 'total_mass_source': r'$M_T^{src}[M_{\odot}]$'
              , 'chi_eff': r'$\chi_\mathrm{eff}$'
              , 'luminosity_distance': r'$d_L$[Mpc]'
              , 'redshift': r'$z$'
              , 'theta_jn': r'$\theta_\mathrm{JN}$[rad]'
              ,'eccentricity':r'$e_0$'
              ,'mean_anomaly':r'$\zeta_0$'
              ,'mean_per_ano':r'$\zeta_0$'
              ,'e_gw':r'$e_{\mathrm{gw}}$'
              ,'l_gw':r'$l_{\mathrm{gw}}$'
              }
""";

colors=['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']

colors = ['#1E90FF','#DC143C','#7CFC00','#8A2BE2','#ff8f00','#002147'
          ,'#A3C1AD','#293133','#ff0038','#F0D077','#006699','#c90016','#0f4d92','#666666',
          '#50C878','#D80010','#7CEECE'
          ,'#1EB53A','#DA0A14','#00A1E4','#7BB135','#000000','#FF6C0C']
colors= ['#4C72B0', 
         '#DD8452' 
         , '#937860' 
    ,'#DA8BC3' 
    ,'#55A868' 
        ]

def read_inj_file(injection_file):
    """
    Function to read injection file used to create a frame file.
    """
    
    
    with open(injection_file) as json_file:
        injection_params= json.load(json_file)
        

    injection_params['total_mass']=injection_params['mass_1']+injection_params['mass_2']
    injection_params = bilby.gw.conversion.convert_to_lal_binary_black_hole_parameters(injection_params)[0]

    injection_params['chi_1'] = injection_params['a_1']*np.sin(injection_params['tilt_1'])*np.cos(injection_params['phi_12'])
    injection_params['chi_2'] = injection_params['a_2']*np.sin(injection_params['tilt_2'])*np.cos(injection_params['phi_12'])

    inj_params = bilby.gw.conversion.generate_all_bbh_parameters(injection_params)

    
    return inj_params




def generate_inj_dict(result):
    """
    Create the injection dictionary from the Bilby posterior file. It only works when the injection has been done using Bilby.
    """
        
    # Generate injection dictionary
    posterior_dict ={}
    inj_dict = {}
    for key in result.keys():
        posterior_dict[key] = result[key].posterior
        inj_params =  bilby.gw.conversion.convert_to_lal_binary_black_hole_parameters(result[key].injection_parameters)[0]
        inj_dict[key] = bilby.gw.conversion.generate_all_bbh_parameters(inj_params)


        if inj_dict[key]['mass_1']<inj_dict[key]['mass_2']:
            inj_dict[key]['mass_ratio'] = 1./inj_dict[key]['mass_ratio']

    return inj_dict 

def read_posteriors(files:list):

    basename_list = [os.path.basename(file0).split('.hdf5')[0].split('_merged')[0] for file0 in files]
    #basename_list = ['SEOBNRv5E']#, 'SEOBNRv5E old']
    tag_list = basename_list#[file0.split('q4_05_m01_e0_inj_')[1] for file0 in basename_list]

    tag_dict ={}
    result = {}
    result_plot_dict = {}
    for ii in range(len(basename_list)):
        file0 = files[ii]
        
        name =tag_list[ii]# basename_list[ii]
        tag_dict[name] = tag_list[ii]
        
        print(name)
        result[name] = bilby.read_in_result(file0)
        detectors = list (result[name].meta_data['likelihood']['interferometers'].keys())
        
        matched_filter_snr =0
        for det in detectors:
            matched_filter_snr += abs(result[name].posterior[det+'_matched_filter_snr'])**2.
        result[name].posterior['network_matched_filter_snr'] = np.sqrt( matched_filter_snr) 
        
        keys = list(result[name].posterior.keys())

        if 'mean_anomaly' not in keys and 'mean_per_ano' in keys:
            result[name].posterior['mean_anomaly'] = result[name].posterior['mean_per_ano']
        
        if 'mean_per_ano' not in keys and 'mean_anomaly' in keys:
            result[name].posterior['mean_per_ano'] = result[name].posterior['mean_anomaly']
            
        m1 = result[name].posterior['mass_1']
        m2 = result[name].posterior['mass_2']
        m1_src = result[name].posterior['mass_1_source']
        m2_src = result[name].posterior['mass_2_source']

        result[name].posterior['mass_1'] = m2
        result[name].posterior['mass_2'] = m1
        result[name].posterior['mass_1_source'] = m2_src
        result[name].posterior['mass_2_source'] = m1_src

        result_plot_dict[name] = result[name].posterior
        print('=====================================================')

    return result, result_plot_dict, tag_dict


# Functions to plot model-model injections
def posterior_comparison_inj(parameter,
                             result_dict,
                             outdir='./outdir/',
                             plot_injection=True,
                             label='test',
                             labels_legend_dict=None,
                             ylabel=True,
                            legend=True,
                            pos_legend=None,
                             ls_styles = None,
                             lw_styles = None,
                            legend_size=13,colors =  ['#4C72B0',  '#DD8452', '#937860','#DA8BC3' ,'#55A868'],
                             ylims= None, xlims= None,
                             inj_dict=None,
                             save_plot = False
                            ):
    """
    Function to plot 1D posteriors
    """
    

    posterior_dict ={}
    for key in result_dict.keys():
        posterior_dict[key] = result_dict[key].posterior 
    
    fig,ax = plt.subplots(figsize=(6,4),dpi=250)
    
     
    idx = 0
    for key in posterior_dict.keys():
        
        posterior = posterior_dict[key]
        pos_keys = posterior.keys()
        
        if ls_styles:
            ls = ls_styles[idx]
            lw = lw_styles[idx]
        else:
            ls = '-'
            lw=histlw
        if parameter in pos_keys:
            
            posterior = posterior_dict[key][parameter]
            Pr_Default_Lower  = np.percentile(posterior,10)
            Pr_Default_Upper  = np.percentile(posterior,90)
            best=np.median(posterior)
            lowerp=np.abs(Pr_Default_Lower-best)
            upperp=Pr_Default_Upper-best

            
            if labels_legend_dict:
                key_plot = labels_legend_dict[key]

            else:
                key_plot = key

            sns.histplot(data=posterior, 
                         element="step",
                         stat='density',
                         #bins=75,
                         color=colors[idx],
                         fill=False,
                         linewidth=histlw, alpha=alhist,label=key_plot)
            
            plt.axvline(Pr_Default_Lower, ls = '--', c = colors[idx], lw=lw)
            plt.axvline(Pr_Default_Upper, ls = '--', c = colors[idx], lw=lw)


        idx += 1
        
    if(plot_injection) and (inj_dict):
        plt.axvline(inj_dict[key][parameter], ls = '-', c = 'k', lw=2, 
                    label='Inj. value ')#+key)
    #else:
    #    plt.title(r"$%s^{+%s}_{-%s}$" % (np.round(best,2),np.round(lowerp,2),np.round(upperp,2)))
    
    plt.xlabel(key_labels[parameter],fontsize=20);
    if ylabel:
        plt.ylabel('Probability Density',fontsize=20);
    
    
    size=20
    ax.tick_params(axis='x', which='major', pad=8,width=1.5,length=2,  size=3, labelsize=size,direction='in')
    ax.tick_params(axis='x', which='minor', pad=8,width=1,  length=1.5,size=1.5, labelsize=size,direction='in')
    ax.tick_params(axis='y', which='major', pad=8,width=1.5,length=2,  size=3, labelsize=size,direction='in')
    ax.tick_params(axis='y', which='minor', pad=8,width=1., length=1.5,size=1.5, labelsize=size,direction='in')


    
    if legend :
        if pos_legend:
            plt.legend(loc = 'best',frameon=False, prop={'size': legend_size}, bbox_to_anchor=pos_legend,
                      handlelength=1);
        else:
            plt.legend(loc = 'best',frameon=False, prop={'size':legend_size},handlelength=1);            
    if ylims:
        ax.set_ylim(ylims[0],ylims[1])
    if xlims:
        ax.set_xlim(xlims[0],xlims[1])
         
    plt.tight_layout()

    

    if save_plot:
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        plt.savefig(outdir+label+'_posterior_%s.png'%parameter, bbox_inches = 'tight')
        plt.savefig(outdir+label+'_posterior_%s.pdf'%parameter, bbox_inches = 'tight')


##### Functions to plot 2D posteriors
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def round_limit(max_val):
    if max_val < 1:
        max_x_str = str(max_val)
        digits = len(re.search('\d+\.(0*)', max_x_str).group(1))
        return(truncate(max_val, decimals=digits+1))
    else:
        return(truncate(max_val, decimals = 0))

#-------------------------------------------
# a. Plot with 2D contour + x,y histogram
#-------------------------------------------
def triangle_plot_2d_axes(
    xbounds, ybounds, figsize=(8, 8),
    width_ratios=[4, 1], height_ratios=[1, 4], wspace=0.0, hspace=0.0,
    grid=False,high1d=1):
    """Initialize the axes for a 2d triangle plot.
    """
    high1d = high1d

    fig = plt.figure(figsize=figsize, dpi=200)
    gs = gridspec.GridSpec(
        2, 2,
        width_ratios=width_ratios, height_ratios=height_ratios,
        wspace=wspace, hspace=hspace)

    ax1 = plt.subplot(gs[0])
    ax3 = plt.subplot(gs[2])
    ax4 = plt.subplot(gs[3])

    ax1.minorticks_on()
    ax3.minorticks_on()
    ax4.minorticks_on()

    if grid:
        ax1.grid(which='major', ls='-')
        ax1.grid(which='minor', ls=':')
        ax3.grid(which='major', ls='-')
        ax3.grid(which='minor', ls=':')
        ax4.grid(which='major', ls='-')
        ax4.grid(which='minor', ls=':')

    # Get rid of tick labels
    ax1.xaxis.set_ticklabels([])
    ax4.yaxis.set_ticklabels([])

    # Use consistent x-axis and y-axis bounds in all 3 plots
    ax1.set_ylim(0, high1d)
    ax1.set_xlim(xbounds[0], xbounds[1])
    ax3.set_xlim(xbounds[0], xbounds[1])
    ax3.set_ylim(ybounds[0], ybounds[1])
    ax4.set_xlim(0, high1d)
    ax4.set_ylim(ybounds[0], ybounds[1])

    return fig, ax1, ax3, ax4


def create_fig_and_axes(xbounds, ybounds, figsize=(6, 6),high1d=1):
    fig, ax1, ax3, ax4 = triangle_plot_2d_axes(
        xbounds, ybounds, figsize=figsize, width_ratios=[4, 1],grid=False,
        height_ratios=[1, 4], wspace=0.0, hspace=0.0,high1d=high1d)
    return fig, ax1, ax3, ax4

#------------------------------------------------------------
# b. Plotting the main result: NRSur PHM (filled Contour)
#------------------------------------------------------------

def add_samples_to_fig_hist(name,samples_dict, parameter_1,parameter_2,xlims,ylims,color_dict, label_dict, alpha_dict, lw_dict, bins_dict,ax1,ax3,ax4, zorder=10,norm_factor_x=1,norm_factor_y=1,lwcontour=4, contourdict={}, inj_values = None):

    #name: name of pe result to plot
    #parameter 1 and parameter 2: parameters to plot in the 2D plot
    #zorder: if plottting multiple results, a larger zorder places the contour on top
    #norm_factor_x,y: parameter to scale the corner 1D histograms

    x = np.array(samples_dict[name][parameter_1])
    y = np.array(samples_dict[name][parameter_2])
    xlow, xhigh = xlims
    xsmooth = np.linspace(xlow, xhigh, 1000)
    ylow, yhigh = ylims
    ysmooth = np.linspace(ylow, yhigh, 1000)

    norm_factor_x=0.95*norm_factor_x
    norm_factor_y=0.95*norm_factor_y

    c = color_dict[name]
    label = label_dict[name]
    alpha = alpha_dict[name]
    lw = lw_dict[name]
    kde = gaussian_kde(x)
    max_val_x = max(kde(xsmooth))
    bb = bins_dict[name]

    #ax1.plot(xsmooth, norm_factor_x*kde(xsmooth), color=c, lw=lw, label=label,zorder=zorder)
    #ax1.fill_between(xsmooth, 0, norm_factor_x*kde(xsmooth), color=c, alpha=alpha,zorder=zorder)
    #ax1.hist(norm_factor_x*xsmooth, bins = 50, density = True, histtype='stepfilled', color=c, label=label)
    sns.histplot(x, bins=80, kde=False, stat='density', lw= lw,alpha= alpha, color= c, element="step",fill= True, ax=ax1)
    sns.histplot(x, bins=80, kde=False, stat='density',lw= lw, color= c, fill= False, element="step", ax=ax1)

    ax1.set_ylabel("")
    ax1.set_xlabel("")


    ax1.axvline(np.quantile(x, 0.05), color=c, ls='dashed')
    ax1.axvline(np.quantile(x, 0.95), color=c, ls='dashed')
    ax1.set_ylim((0,norm_factor_x*1.1))
    
    kde = gaussian_kde(y)
    max_val_y = max(kde(ysmooth))
    #ax4.plot(norm_factor_y*kde(ysmooth), ysmooth, color=c, lw=lw, label=label,zorder=zorder)
    #ax4.hist(norm_factor_y*ysmooth, bins = 50, histtype='stepfilled', color=c, label=label)

    sns.histplot(y=y, bins=80, kde=False, stat='density', lw= lw,alpha= alpha, color= c, element="step", fill= True,  ax=ax4)#, orientation='horizontal')
    sns.histplot(y=y, bins=80, kde=False, stat='density',lw= lw,color= c, fill= False,  element="step", ax=ax4)#, orientation='horizontal')
    #ax4.fill_betweenx(ysmooth, 0, norm_factor_y*kde(ysmooth), color=c, alpha=alpha,zorder=zorder)
    ax4.axhline(np.quantile(y, 0.05), color=c, ls='dashed')
    ax4.axhline(np.quantile(y, 0.95), color=c, ls='dashed')

    ax4.set_ylabel("")
    ax4.set_xlabel("")
    ax4.set_xlim((0,norm_factor_y*1.1))
    

    ax1.grid(False)
    ax4.grid(False)
    #the level=0.9 parameter, makes the 2D contours enclose the 90% of the posterior volume/surface.

    my_range = [[xlow, xhigh], [ylow, yhigh]]

    # sns.histplot(x=x, y=y, bins=bb, ax=ax3, color=c, stat='count', cbar=True, fill=True, 
    #          pthresh=0.9, levels=[0.9], contour=True, contour_kws={'linewidths': lwcontour, **contourdict})
    
    # sns.kdeplot(x=x, y=y, bins=bb, ax=ax3, color=c, stat='count', fill=True, cbar=False,
    #          pthresh=0.9, levels=(np.exp(-1),np.exp(-0.5)), contour=True, contour_kws={'linewidths': lwcontour, **contourdict})

    sns.kdeplot(x=x, y=y, bins=bb, ax=ax3, color=c, stat='density', fill=True, alpha=alpha,
             pthresh=0.9,  contour=True, contour_kws={'linewidths': lwcontour, **contourdict})
    
    sns.kdeplot(x=x, y=y, bins=bb, ax=ax3, color=c, stat='density', fill=False, 
             pthresh=0.9)
    

#     corner.hist2d(x, y, ax=ax3, range=my_range, color=c,
#                   plot_datapoints=False, plot_density=True,smooth=True,#levels=(np.exp(-0.5),np.exp(-1)),
#                   levels=[0.9],fill_contours=False,bins=bb, lw=lwcontour, contour_kwargs=contourdict
# #                   fill_contours=False, no_fill_contours=False,
#                   #contour_kwargs=dict(linewidth=4)
#                  )

#----------------------------------------------------------------------------
# c. Plotting other models: Phenom PHM, SEOBNR PHM (transparent contours)
#-----------------------------------------------------------------------------

def add_samples_to_fig_nofilled_hist(name, samples_dict, parameter_1,parameter_2,xlims,ylims,color_dict, label_dict, alpha_dict, lw_dict, bins_dict,ax1,ax3,ax4, zorder=10,norm_factor_x=1,norm_factor_y=1, lwcontour=4, contourdict={}):

    x = np.array(samples_dict[name][parameter_1])
    y = np.array(samples_dict[name][parameter_2])
    xlow, xhigh = xlims
    xsmooth = np.linspace(xlow, xhigh, 1000)
    ylow, yhigh = ylims
    ysmooth = np.linspace(ylow, yhigh, 1000)

    norm_factor_x=0.95*norm_factor_x
    norm_factor_y=0.95*norm_factor_y

    c = color_dict[name]
    label = label_dict[name]
    alpha = alpha_dict[name]
    lw = lw_dict[name]
    kde = gaussian_kde(x)
    max_val_x = max(kde(xsmooth))
    bb = bins_dict[name]

    #ax1.plot(xsmooth, norm_factor_x*kde(xsmooth), color=c, lw=lw, label=label,zorder=zorder)
    #ax1.hist(norm_factor_x*xsmooth, bins = 50, density = True, histtype='step', color=c, label=label)
    ax1.hist(x, bins=80,density=True,histtype='step',color=c,lw=lw,label=label)

    ax1.axvline(np.quantile(x, 0.05), color=c, ls='dashed')
    ax1.axvline(np.quantile(x, 0.95), color=c, ls='dashed')
    ax1.set_ylim((0,norm_factor_x))

    kde = gaussian_kde(y)
    max_val_y = max(kde(ysmooth))

    #ax4.plot(norm_factor_y*kde(ysmooth), ysmooth, color=c, lw=lw, label=label,zorder=zorder)
    #ax4.hist(norm_factor_x*ysmooth, bins = 50, density = True, histtype='step', color=c, label=label)
    ax4.hist(y, bins=80, orientation='horizontal',density=True,histtype='step',color=c,lw=lw,label=label)
    ax4.axhline(np.quantile(y, 0.05), color=c, ls='dashed')
    ax4.axhline(np.quantile(y, 0.95), color=c, ls='dashed')
    ax4.set_xlim((0,norm_factor_y))

    my_range = [[xlow, xhigh], [ylow, yhigh]]
    corner.hist2d(x, y, ax=ax3, range=my_range, color=c,
                  plot_datapoints=False, plot_density=False,smooth=True,
                  levels=[0.9],no_fill_contour=False,bins=bb, lw=lwcontour, contour_kwargs=contourdict
                 )

def corner_plots_hist_SNS(result_posteriors, parameter_1, parameter_2, outdir,colors,no_solid=[],ncol=1, lw=1.5,lwcontour=4, alpha = 0.2, 
                      bins = 50, norm_factor = 1.60, save_plot=True, plotMaxL=False, loclegends='upper left', bboxlegend=(1.25, 1), xlims=None, 
                      ylims=None, contour_linewidth=2,legend_size = 12 ,xlabel=None, ylabel=None, fontsize = 24,
                      contour_linestyle='solid',showLegend=False,annotate='',annotate_position=(0.12,0.12),label_plot='GWXXXX', inj_dict = None, inj_dict_list = None):

    label_dict = {}
    color_dict = {}
    alpha_dict = {}
    lw_dict = {}
    bins_dict = {}
    contour_linewidth_dict = {}
    contour_linestyle_dict = {}
    if not isinstance(contour_linewidth,list):
        contour_linewidth = [contour_linewidth]*len(result_posteriors)
    if not isinstance(contour_linestyle,list):
        contour_linestyle = [contour_linestyle]*len(result_posteriors)

    for ind,key in enumerate(result_posteriors.keys()):
        label_dict[key]=key
        color_dict[key]=colors[ind]
        alpha_dict[key]=alpha
        bins_dict[key]=bins
        lw_dict[key]=lw
        contour_linewidth_dict[key] = contour_linewidth[ind]
        contour_linestyle_dict[key] = contour_linestyle[ind]

    xmin_list = []
    xmax_list = []
    ymin_list = []
    ymax_list = []

    for key in result_posteriors.keys():
        x = result_posteriors[key][parameter_1]
        y = result_posteriors[key][parameter_2]

        xmin = x.min()
        xmax = x.max()
        ymin = y.min()
        ymax = y.max()

        xmin_list.append(xmin)
        xmax_list.append(xmax)
        ymin_list.append(ymin)
        ymax_list.append(ymax)

    if xlims is None:
        xlims = [min(xmin_list),max(xmax_list)]
    if ylims is None:
        ylims = [min(ymin_list),max(ymax_list)]

    #if parameter_2 is 'log_likelihood':
    #    ylims = [0,max(ymax_list)+1]

    fig, ax1, ax3, ax4 = create_fig_and_axes(xlims, ylims)

    #ax3.set_xlabel(key_labels[parameter_1],fontsize=24)
    #ax3.set_ylabel(key_labels[parameter_2],fontsize=24)
    if xlabel:
        ax3.set_xlabel(xlabel,fontsize=fontsize)
    else:
        ax3.set_xlabel(key_labels[parameter_1],fontsize=fontsize)

    if ylabel:
        ax3.set_ylabel(ylabel,fontsize=fontsize)
    else:
        ax3.set_ylabel(key_labels[parameter_2],fontsize=fontsize)

    ax3.tick_params(labelsize=10)

    #ax3.set_xlabel(key_labels[parameter_1],fontsize=18)
    #ax3.set_ylabel(key_labels[parameter_2],fontsize=18)
    #ax3.tick_params(labelsize=8)#,direction='in')

    if parameter_1 == 'mass_ratio' or parameter_2 == 'mass_ratio':
        add = 0
    else:
        add = 1
    my_array_x=np.linspace(xlims[0]-add,xlims[1]+add,1000)
    my_array_y=np.linspace(ylims[0]-add,ylims[1]+add,1000)

    rx = []
    ry = []

    for key in result_posteriors.keys():

        xdat = result_posteriors[key][parameter_1]
        # Plot the histogram using seaborn and get the maximum density value
        ax = sns.histplot(xdat, bins=80, kde=False, stat='density', fill=True)
        hist_values = [patch.get_height() for patch in ax.patches]  # Get density values from the bars
        # Get the maximum density value
        rxi = np.max(hist_values)
        rx.append(rxi)

        # ydat
        ydat = result_posteriors[key][parameter_2]
        # Plot the histogram using seaborn and get the maximum density value
        ax = sns.histplot(y=ydat, bins=80, kde=False, stat='density', fill=True)
        hist_values = [patch.get_height() for patch in ax.patches]  # Get density values from the bars
        # Get the maximum density value
        rxi = np.max(hist_values)
        ry.append(rxi)

    norm_factor_x = max(rx)
    norm_factor_y = max(ry)

    for key in result_posteriors.keys():

        if key in no_solid:
            add_samples_to_fig_nofilled_hist(key,result_posteriors,parameter_1,parameter_2,xlims,ylims,color_dict,
            label_dict, alpha_dict, lw_dict, bins_dict, ax1,ax3,ax4,zorder=20,
            norm_factor_x=round_limit(norm_factor_x),norm_factor_y=round_limit(norm_factor_y),
            lwcontour=lwcontour,contourdict={'linewidths':contour_linewidth_dict[key], 'linestyles':contour_linestyle_dict[key]})
        else:
            add_samples_to_fig_hist(key,result_posteriors,parameter_1,parameter_2,xlims,ylims,color_dict,
            label_dict, alpha_dict, lw_dict, bins_dict, ax1,ax3,ax4,zorder=20,
            norm_factor_x=round_limit(norm_factor_x),norm_factor_y=round_limit(norm_factor_y),
            lwcontour=lwcontour,contourdict={'linewidths':contour_linewidth_dict[key], 'linestyles':contour_linestyle_dict[key]})


    if inj_dict != None:
        ax1.axvline(x = inj_dict[parameter_1],ls = '-',color='gray',lw=lw)
        ax3.axvline(x = inj_dict[parameter_1],ls = '-',color='gray',lw=lw)
        ax4.axhline(y = inj_dict[parameter_2],ls = '-',color='gray',lw=lw)
        ax3.axhline(y = inj_dict[parameter_2],ls = '-',color='gray',lw=lw)
        
        ax3.scatter(inj_dict[parameter_1],inj_dict[parameter_2], s = 15,color='gray',lw=lw, marker='s')
    if inj_dict_list != None:

        for key in result_posteriors.keys():

            ax1.axvline(x = float(inj_dict_list[key][parameter_1]),ls = '-',color=color_dict[key],lw=lw)
            ax3.axvline(x = float(inj_dict_list[key][parameter_1]),ls = '-',color=color_dict[key],lw=lw)
            ax4.axhline(y = float(inj_dict_list[key][parameter_2]),ls = '-',color=color_dict[key],lw=lw)
            ax3.axhline(y = float(inj_dict_list[key][parameter_2]),ls = '-',color=color_dict[key],lw=lw)
            
            ax3.scatter(inj_dict_list[key][parameter_1],inj_dict_list[key][parameter_2], s = 15,color=color_dict[key], edgecolor='k',lw=lw, marker='X')


    if plotMaxL:
        for key in result_posteriors.keys():
            maxLpos = np.argmax(result_posteriors[key]['log_likelihood'].values)
            par1maxL = result_posteriors[key][parameter_1].values[maxLpos]
            par2maxL = result_posteriors[key][parameter_2].values[maxLpos]
            ax3.plot(par1maxL,par2maxL,marker='*', markersize=21, color=color_dict[key], markeredgecolor='black',markeredgewidth=1.0, linewidth=3)
    
    ax3.set_xlim(*xlims)
    ax1.set_yticklabels([],fontsize=10)
    ax4.set_xticklabels([],fontsize=20)
    if showLegend:
        ax3.legend(*ax4.get_legend_handles_labels(), loc=loclegends,bbox_to_anchor=bboxlegend, frameon=False,prop={'size': legend_size},ncol=ncol,handlelength=1)
    ax3.tick_params(axis='both', labelsize=20)
    
    ax3.annotate(annotate, xy=annotate_position, xycoords='axes fraction', fontsize = fontsize)#'x-large')
    if parameter_1 == 'mass_1_source' and parameter_2 == 'mass_2_source':

    
        xblack = [0,0,1000]
        yblack = [0,1000,1000]
        ax3.fill(xblack, yblack, 1000,facecolor='C7',zorder=10)

    
    ax3.grid(False)
    

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    if save_plot:
        fig.savefig(outdir+'/cornerPlot_'+label_plot+'_'+parameter_1+'_'+parameter_2+'.png', transparent=True, bbox_inches='tight')
        #fig.savefig(outdir+'/cornerPlot_'+label_plot+'_'+parameter_1+'_'+parameter_2+'.pdf', transparent=True, bbox_inches='tight')
