<?xml version="1.0" encoding="UTF-8"?>
<!--
Принцип именования полей:
название-поля_тип, где
    название поля - название поля, например local-number. В название не должно содержаться символ "_", так как он является
                    разделителем.
    тип - тип поля, тип содержимого, например local-nuber_s
    "_" - разделитель типа и название.

Типы:
s - неделимая строка
t - текст
dt - дата

-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml"/>

<!--<xsl:template match="/">
    <add>
        <xsl:for-each select="record">
            <xsl:apply-templates select="record"/>
        </xsl:for-each>
    </add>
</xsl:template>-->


<xsl:output indent="yes" method="xml" version="1.0" encoding="UTF-8"/>

<!-- disable all default text node output -->
<xsl:template match="text()"/>

<xsl:template match="/">
    <xsl:if test="collection">
        <collection>
            <xsl:apply-templates select="collection/record"/>
        </collection>
    </xsl:if>
    <xsl:if test="record">
        <xsl:variable name="leader7" select="leader/leader07"/>

        <xsl:apply-templates select="record"/>
    </xsl:if>
</xsl:template>

<!-- match on marcxml record -->
<xsl:template match="record">
    <xsl:variable name="f105_a" select="field[@id='105']/subfield[@id='a']"/>
    <!--<xsl:value-of select="substring($f105_a,20,1)"/>-->
    <doc>
        <xsl:call-template name="document_id"/>
        <xsl:call-template name="authorities"/>
</doc>
</xsl:template>
<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="document_id">
    <xsl:for-each select="gen_id[1]">
        <field name="id">
            <xsl:value-of select="."/>
        </field>
    </xsl:for-each>
</xsl:template>

<xsl:template name="authorities">
    <xsl:call-template name="Local-number"/>
    <xsl:call-template name="Person-name"/>
    <xsl:call-template name="Source-title"/>
    <xsl:call-template name="Subject-heading"/>
    <xsl:call-template name="Subject-subheading"/>
    <!--<xsl:call-template name="Subject-hierarhy"/>-->
    <xsl:call-template name="General-note"/>
</xsl:template>






<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Local-number">
    <xsl:for-each select="field[@id='001']">
        <field name="local_number_s">
            <xsl:value-of select="."/>
        </field>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

<xsl:template name="Person-name">
    <xsl:for-each select="field[@id='200']">
        <!--<xsl:variable name="sf_a" select="subfield[@id='a'][1]"/>
        <xsl:variable name="sf_b" select="subfield[@id='b'][1]"/>
        <xsl:variable name="sf_g" select="subfield[@id='g'][1]"/>
            <field name="person_name_t">
                <xsl:value-of select="$sf_a"/><xsl:text> </xsl:text><xsl:value-of select="$sf_b"/>
            </field>
            <field name="person_name_t">
                <xsl:value-of select="$sf_a"/><xsl:text> </xsl:text><xsl:value-of select="$sf_g"/>
            </field>-->
        <xsl:if test="subfield[@id='a']">
            <field name="person_name">
                <xsl:value-of select="subfield[@id='a']"/>
                <xsl:if test="subfield[@id='b']">
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="subfield[@id='b']"/>
                </xsl:if>
                <xsl:if test="not(subfield[@id='b']) and subfield[@id='g']">
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="subfield[@id='g']"/>
                </xsl:if>
            </field>
        </xsl:if>
    </xsl:for-each>
</xsl:template>

<xsl:template name="Subject-heading">
    <xsl:for-each select="field[@id='250']">
        <xsl:for-each select="subfield[@id='a']">
            <field name="subject_heading_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>

<xsl:template name="Subject-subheading">
    <xsl:for-each select="field[@id='250']">
        <xsl:for-each select="subfield[@id='x']">
                <field name="subject_subheading_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>


<xsl:template name="Subject-hierarhy">
    <xsl:for-each select="field[@id='250']">
            <field name="subject_hierarhy_dp">
                <xsl:value-of select="subfield[@id='a']"/>
                <xsl:text>/</xsl:text>
                <xsl:value-of select="subfield[@id='x']"/>
            </field>
    </xsl:for-each>
</xsl:template>


<xsl:template name="Source-title">
    <xsl:for-each select="field[@id='810']">
        <field name="source_title_t">
            <xsl:value-of select="subfield[@id='a']"/>
        </field>
    </xsl:for-each>
</xsl:template>

<xsl:template name="General-note">
    <xsl:for-each select="field[@id='830']">
        <xsl:for-each select="subfield[@id='a']">
            <field name="general_note_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->



</xsl:stylesheet>



