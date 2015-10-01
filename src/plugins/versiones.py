# -*- coding: utf-8 -*-
# Copyright 2015 - Pedro Boliche <bolichep@gmail.com>
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

import info_table
import glob
import re
#from subprocess import check_output, Popen, PIPE
from subprocess import check_output

##### BORRAR!!!!!
# row -> present
### 0
label_start_markup = '<span font_style="normal" font_weight="bold" color="black">'
label_end_markup   = '</span>'
text_start_markup  = '<span size="smaller" color="black">'
text_end_markup    = '</span>'
### 1
def label_set_markup(label):
	return label_start_markup + label + label_end_markup
### 1
def text_set_markup(text):
	return text_start_markup + text + text_end_markup

##### BORRAR!!!!!




# present -> suites -> sources
### 1
def get_sources():
   allsources = glob.glob('/etc/apt/sources.list.d/*.list')
   allsources.insert(0, '/etc/apt/sources.list' )

   result = ''
   for src in allsources:
      try:
         result += open(src).read()
      except:
         pass

   return result
### 1
def proc_found(raw, done, distro):
	if distro in raw:
		done.append( distro )
		raw.remove( distro )

	return raw, done
### 2
def found_suites_from_sources():
   sources = get_sources()

   found = list ( set ( re.findall(r'^\s*deb(?:\s+\[.*\])?\s+(?:(?:https?://)|(?:ftp://))?(?:(?:[\w])+(?:[\./]+)?)+\s([-\w/]+).*$', sources, re.MULTILINE ) ) )

   huayra_suites = [ 'brisa','mate-brisa','pampero','mate-pampero','sud','torbellino' ]
   huayras = []
   for suite in huayra_suites:
	   found, huayras = proc_found( found , huayras, suite )
	   found, huayras = proc_found( found , huayras, suite + '-updates' )
	   found, huayras = proc_found( found , huayras, suite + '-proposed' )

   deb_suites = [ 'squeeze','oldoldstable','wheezy','oldstable','jessie','stable','stretch','testing','sid','unstable','experimental','rc-buggy' ]
   debians = []
   for suite in deb_suites:
	   found, debians = proc_found( found , debians, suite )
   	   found, debians = proc_found( found , debians, suite + '-updates' )
	   found, debians = proc_found( found , debians, suite + '/updates' )
	   found, debians = proc_found( found , debians, suite + '-proposed-updates' )
   	   found, debians = proc_found( found , debians, suite + '-backports' )


   huayra = ",".join(str(i) for i in huayras)
   debian = ",".join(str(i) for i in debians)
   resto  = ",".join(str(i) for i in found)

   return huayra, debian, resto
### 3
def check_sources_debian():
	nil, debian_sources_repos, nil = found_suites_from_sources()
	return debian_sources_repos
### 3
def check_sources_huayra():
	huayra_sources_repos, nil, nil = found_suites_from_sources()
	return huayra_sources_repos
#

# armado de versiones
### 2 
def huayra():

  lsb_release = check_output(['lsb_release','-sirc']).split()
  if lsb_release[0] == 'Huayra': ### lsb_release is aware of huayra
    huayra_raw_ver = lsb_release[1]
    huayra_code_name = lsb_release[2]
  else:
    try:
      huayra_raw_ver = open('/etc/huayra_version','r').read()[:-1]
      if huayra_raw_ver >= "3.0" :
        huayra_code_name = 'sud'
      elif huayra_raw_ver >="2.0" :
        huayra_code_name = 'pampero'
    except IOError as e: ### huayra is not still aware of himself
      huayra_code_name = 'brisa'
      huayra_raw_ver = '1.X'

  # ? hay repos agregados ?
  huayra_sources_repos =  check_sources_huayra()
  if huayra_code_name != huayra_sources_repos :
     huayra_sources_repos = '[' + huayra_sources_repos + ']'
  else:
     huayra_sources_repos = ''

  huayra_label = label_set_markup ( 'Versión' )
  huayra_text = text_set_markup ( 'Huayra ' + huayra_raw_ver + ' (' + huayra_code_name +') ' +  huayra_sources_repos )

  return huayra_label,huayra_text

### 2
def debian():

  base_src_code_name = check_sources_debian()
  try:
     base_dist_ver = open('/etc/debian_version','r').read().split()
  except:
     base_dist_ver = ['']

  base_dist_issue = ['Debian']
  debian_label = label_set_markup( 'Base' )
  debian_text = text_set_markup( base_dist_issue[0] + ' ' + base_dist_ver[0] + ' [' + base_src_code_name + ']' )
  return debian_label, debian_text
###
def kernel():

  running_kernel = check_output(['uname','-r','-v']).split()
  krel_label = label_set_markup( 'Kernel lanzamiento' )
  krel_text = text_set_markup ( running_kernel[0] )
  kver_label = label_set_markup( 'Kernel versión')
  kver_text = text_set_markup( running_kernel[3] + ' ' + running_kernel[4] )

  return krel_label, krel_text, kver_label, kver_text

info_table.add_row_to_table( huayra()[0], huayra()[1] , 0 , "Versión de Huayra\n[Repositorios habilitados]" )
info_table.add_row_to_table( debian()[0], debian()[1] , 1 , "Versión base de Debian\n[Repositorios habilitados]" )
info_table.add_row_to_table( kernel()[2], kernel()[3] , 5 , "Versión de compilación del kernel" )

print __name__