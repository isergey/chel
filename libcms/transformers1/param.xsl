<?xml version="1.0" encoding="utf-8"?>
<!--
 * $Log: param.xsl,v $
 * Revision 1.10  2003/11/12 19:41:13  rustam
 * Downloading of selected records
 *
 * Revision 1.9  2003/10/20 08:26:56  rustam
 * Minor changes
 *
 * Revision 1.8  2003/10/20 07:33:56  rustam
 * Minor changes
 *
 * Revision 1.7  2003/09/30 11:27:15  rustam
 * Implemented resource control
 *
 * Revision 1.6  2003/09/16 07:27:20  rustam
 * Added parameter item.order
 *
 * Revision 1.5  2003/09/02 09:08:45  rustam
 * Implemented record syntax selection simplification
 *
 * Revision 1.4  2003/05/15 10:40:55  rustam
 * Minor changes
 *
 * Revision 1.3  2003/05/15 07:27:37  rustam
 * Implemented profiles
 *
 * Revision 1.2  2003/03/27 10:58:26  rustam
 * Added support for external selector dialog
 *
 * Revision 1.1  2003/01/31 14:11:50  rustam
 * New pre-release
 *
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> 

<!-- Common parameters -->
<xsl:param name="lang" select="'eng'"/>
<xsl:param name="charset" select="'UTF-8'"/>
<xsl:param name="session.id" select="''"/>
<xsl:param name="target" select="''"/>
<xsl:param name="cgi.script.URL" select="'zgate'"/>
<xsl:param name="stylesheet.URL" select="'/ss/zgate.css'"/>
<xsl:param name="ZURL.resolver" select="'zurlhtml'"/>
<xsl:param name="attribute.set" select="'1.2.840.10003.3.1'"/>
<xsl:param name="ad" select="document('attr.xml')"/>

<!-- Form creation parameters -->
<xsl:param name="msg.form" select="document('form_msg.xml')"/>
<xsl:param name="ed" select="document('expand.xml')"/>
<xsl:param name="ld" select="document('lang.xml')"/>
<xsl:param name="md" select="document('materials.xml')"/>
<xsl:param name="help.URL" select="'http://obs.ruslan.ru/downloads/34.html'"/>
<xsl:param name="java.script.URL" select="'/js/zgate.js'"/>
<xsl:param name="include.help" select="true()"/>
<xsl:param name="include.profiles" select="true()"/>
<xsl:param name="include.ext.form" select="false()"/>
<xsl:param name="include.materials.list" select="true()"/>
<xsl:param name="include.languages.list" select="true()"/>
<xsl:param name="include.recsyn.list" select="false()"/>
<xsl:param name="include.relation.attrs" select="false()"/>
<xsl:param name="include.structure.attrs" select="true()"/>
<xsl:param name="dedup" select="true()"/>
<xsl:param name="sort" select="true()"/>
<xsl:param name="query.expansion" select="true()"/>
<xsl:param name="include.dialog" select="true()"/>
<xsl:param name="include.virtual.kbd" select="true()"/>
<xsl:param name="simplify.recsyn.list" select="true()"/>
<xsl:param name="term.size" select="'35'"/>
<xsl:param name="term.size.max" select="'100'"/>
<xsl:param name="num.records" select="'20'"/>
<xsl:param name="num.records.size" select="'5'"/>
<xsl:param name="list.size" select="'4'"/>
<xsl:param name="element.set.name" select="'B'"/>
<xsl:param name="logo.left.URL" select="''"/>
<xsl:param name="logo.right.URL" select="''"/>
<xsl:param name="query.filter" select="''"/>
<xsl:param name="term.1" select="''"/>
<xsl:param name="term.2" select="''"/>
<xsl:param name="term.3" select="''"/>
<xsl:param name="use.1" select="''"/>
<xsl:param name="use.2" select="''"/>
<xsl:param name="use.3" select="''"/>
<xsl:param name="pda.mode" select="false()"/>
<xsl:param name="onload" select="''"/>
<xsl:param name="extra.template" select="false()"/>
<xsl:param name="extra.header" select="''"/>
<xsl:param name="extra.js" select="''"/>
<xsl:param name="circ.db" select="'circ'"/>

<!-- Workflow and record representation parameters -->
<xsl:param name="fmt" select="'B'"/>
<xsl:param name="result.set.name" select="'default'"/>
<xsl:param name="start" select="1"/>
<xsl:param name="scan.to.form" select="true()"/>
<xsl:param name="hide.diag" select="true()"/>
<xsl:param name="hide.record.warnings" select="true()"/>
<xsl:param name="diag.threshold" select="2"/>
<xsl:param name="max.records" select="10"/>
<xsl:param name="step.size" select="0"/>
<xsl:param name="record.syntax" select="'!'"/>
<xsl:param name="ht" select="true()"/>
<xsl:param name="abstract" select="false()"/>
<xsl:param name="subject" select="false()"/>
<xsl:param name="class" select="false()"/>
<xsl:param name="record.source" select="false()"/>
<xsl:param name="holdings" select="false()"/>
<xsl:param name="marc.labels" select="false()"/>
<xsl:param name="marc.download" select="false()"/>
<xsl:param name="download.all" select="false()"/>
<xsl:param name="download.selected" select="false()"/>
<xsl:param name="follow.subject" select="true()"/>
<xsl:param name="follow.header" select="true()"/>
<xsl:param name="follow.attrs" select="'[1,12]'"/>
<xsl:param name="personal.author.attrs" select="'[1,1004]'"/>
<xsl:param name="corporate.author.attrs" select="'[1,1005]'"/>
<xsl:param name="link.to.related" select="true()"/>
<xsl:param name="link.attrs" select="'[1,1049]'"/>
<xsl:param name="resource.reports" select="false()"/>
<xsl:param name="report" select="'report.html'"/>
<xsl:param name="item.order" select="true()"/>
<xsl:param name="author.link" select="true()"/>
<xsl:param name="schemaId" select="''"/>
<xsl:param name="user.id" select="''"/>
<xsl:param name="profile" select="'simple.xsl'"/>
<xsl:param name="msg" select="document('zgate_msg.xml')"/>
<xsl:param name="org" select="document('zgate_org.xml')"/>
<xsl:param name="dia" select="document('diag.xml')"/>
<xsl:param name="units" select="document('zgate_units.xml')"/>
<xsl:param name="country" select="document('zgate_countries.xml')"/>
<xsl:param name="ia" select="document('zgate_id2addr.xml')"/>
<xsl:param name="order.restriction" select="''"/>
<xsl:param name="circ.desk" select="document('circ_desk.xml')"/>
<xsl:param name="check.records" select="'checkRecords();'"/>
<xsl:param name="org.link.URL" select="''"/>
<xsl:param name="cover" select="'Обложка'"/>
<xsl:param name="opac.holdings.reconstruction" select="false()"/>

</xsl:stylesheet>
