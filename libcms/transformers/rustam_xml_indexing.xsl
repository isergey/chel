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
        <xsl:call-template name="bib1_rules"/>
        <!--<xsl:call-template name="sorting"/>-->
        <xsl:call-template name="systems"/>
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

<xsl:template name="bib1_rules">
    <!-- att 12              Local-number -->
    <xsl:call-template name="Local-number"/>
    <!-- att 1               Personal-name -->
    <!-- att 2               Corporate-name -->
    <!-- att 3               Conference-name -->
    <!-- att 4               Title -->
    <xsl:call-template name="Title"/>
    <!-- att 5               Title-series -->
    <!-- att 6               Title-uniform -->
    <!-- att 7               ISBN -->
    <xsl:call-template name="ISBN"/>
    <!-- att 8               ISSN -->
    <xsl:call-template name="ISSN"/>
    <!-- att 9               LC-card-number -->
    <!-- att 10              BNB-card-number -->
    <!-- att 11              BGF-number -->

    <!-- att 13              Dewey-classification -->
    <!-- att 14              UDC-classification -->
    <!-- att 15              Bliss-classification -->
    <!-- att 16              LC-call-number -->
    <!-- att 17              NLM-call-number -->
    <!-- att 18              NAL-call-number -->
    <!-- att 19              MOS-call-number -->
    <!-- att 20              Local-classification -->
    <!-- att 21              Subject-heading -->
    <xsl:call-template name="Subject-heading"/>
    <xsl:call-template name="Subject-subheading"/>
    <xsl:call-template name="Subject-keywords"/>
    <!-- att 22              Subject-Rameau -->
    <!-- att 23              BDI-index-subject -->
    <!-- att 24              INSPEC-subject -->
    <!-- att 25              MESH-subject -->
    <!-- att 26              PA-subject -->
    <!-- att 27              LC-subject-heading -->
    <!-- att 28              RVM-subject-heading -->
    <!-- att 29              Local-subject-index -->
    <!-- att 30              Date -->
    <!-- att 31              Date-of-publication -->
    <xsl:call-template name="Date-of-publication"/>
    <!-- att 32              Date-of-acquisition -->
    <!-- att 33              Title-key -->
    <!-- att 34              Title-collective -->
    <!-- att 35              Title-parallel -->
    <!-- att 36              Title-cover -->
    <!-- att 37              Title-added-title-page -->
    <!-- att 38              Title-caption -->
    <!-- att 39              Title-running -->
    <!-- att 40              Title-spine -->
    <!-- att 41              Title-other-variant -->
    <!-- att 42              Title-former -->
    <!-- att 43              Title-abbreviated -->
    <!-- att 44              Title-expanded -->
    <!-- att 45              Subject-precis -->
    <!-- att 46              Subject-rswk -->
    <!-- att 47              Subject-subdivision -->
    <!-- att 48              Number-natl-biblio -->
    <!-- att 49              Number-legal-deposit -->
    <!-- att 50              Number-govt-pub -->
    <!-- att 51              Number-music-publisher -->
    <!-- att 52              Number-db -->
    <!-- att 53              Number-local-call -->
    <!-- att 54              Code-language -->
    <xsl:call-template name="Code-language"/>
    <!-- att 55              Code-geographic -->
    <!-- att 56              Code-institution -->
    <!-- att 57              Name-and-title -->
    <!-- att 58              Name-geographic -->
    <!-- att 59              Place-publication -->
    <xsl:call-template name="Place-publication"/>
    <!-- att 60              CODEN -->
    <!-- att 61              Microform-generation -->
    <!-- att 62              Abstract -->
    <!-- <xsl:call-template name="Abstract"/>-->
    <!-- att 63              Note -->
    <!-- att 1000            Author-title -->
    <!-- <xsl:call-template name="Author-title"/>-->
    <!-- att 1001            Record-type -->
    <!-- att 1002            Name -->
    <!-- att 1003            Author -->
    <xsl:call-template name="Author"/>
    <!-- att 1004            Author-name-personal -->
    <!-- <xsl:call-template name="Author-name-personal"/>-->
    <!-- att 1005            Author-name-corporate -->
    <!-- <xsl:call-template name="Author-name-corporate"/>-->
    <!-- att 1006            Author-name-conference -->
    <!-- <xsl:call-template name="Author-name-conference"/>-->
    <!-- att 1007            Identifier-standard -->
    <!-- att 1008            Subject-LC-childrens -->
    <!-- att 1009            Subject-name-personal -->
    <!-- att 1010            Body-of-text -->
    <!-- att 1011            Date/time-added-to-db -->
    <!-- att 1012            Date/time-last-modified -->
    <!-- att 1013            Authority/format-id -->
    <!-- att 1014            Concept-text -->
    <!-- att 1015            Concept-reference -->
    <!-- att 1016            Any -->
    <!-- att 1017            Server-choice -->
    <!-- att 1018            Publisher -->
    <xsl:call-template name="Publisher"/>
    <!-- att 1019            Record-source -->
    <!-- att 1020            Editor -->
    <!-- att 1021            Bib-level -->
    <xsl:call-template name="Bib-level"/>
    <!-- att 1022            Geographic-class -->
    <!-- att 1023            Indexed-by -->
    <!-- att 1024            Map-scale -->
    <!-- att 1025            Music-key -->
    <!-- att 1026            Related-periodical -->
    <!-- att 1027            Report-number -->
    <!-- att 1028            Stock-number -->
    <!-- att 1030            Thematic-number -->
    <!-- att 1031            Material-type -->
    <!-- att 1032            Doc-id -->
    <!-- att 1033            Host-item -->
    <!-- att 1034            Content-type -->
    <xsl:call-template name="Content-type"/>
    <!-- att 1035            Anywhere -->
    <!-- att 1036            Author-Title-Subject -->
</xsl:template>

<xsl:template name="systems">
    <xsl:call-template name="Analitic-title"/>
    <xsl:call-template name="Facet-author"/>
    <xsl:call-template name="Linked-record-number"/>
    <xsl:call-template name="Linked-authority-number"/>
    <xsl:call-template name="Linked-subject-number"/>
    <xsl:call-template name="All"/>
</xsl:template>



<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Subject-heading">
    <xsl:for-each select="field[@id='606']">
        <xsl:if test="indicator[@id ='2'][1]= ' '">
            <xsl:for-each select="subfield[@id='a']">
                <field name="subject_heading_t">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Subject-subheading">
    <xsl:for-each select="field[@id='606']">
        <xsl:if test="indicator[@id ='2'][1]= ' '">
            <xsl:for-each select="subfield[@id='x']">
                <field name="subject_subheading_t">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Subject-keywords">
    <xsl:for-each select="field[@id='610']">
        <xsl:if test="indicator[@id ='2'][1]= ' '">
            <xsl:for-each select="subfield[@id='a']">
                <field name="subject_keywords_t">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
</xsl:template>


<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Date-of-publication">
    <!--
        100##$a поз. 9-12
        100##$a поз. 13-16
        210##$d
    -->
    <xsl:choose>
        <xsl:when test="field[@id='463']/subfield[@id='1']/field[@id='210']/subfield[@id='d']">
            <xsl:for-each select="field[@id='463']/subfield[@id='1']">
                <xsl:call-template name="Extract-Date-of-publication"/>
                <xsl:call-template name="Extract-facet-date-of-publication"/>
            </xsl:for-each>
        </xsl:when>
        <!-- Иначе, извлекаем из основного подполя-->
        <xsl:otherwise>
            <xsl:call-template name="Extract-Date-of-publication"/>
            <xsl:call-template name="Extract-facet-date-of-publication"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->


<xsl:template name="Extract-Date-of-publication">
    <xsl:for-each select="field[@id='100']">
        <xsl:variable name="sf_a_pos_9_12" select="substring(subfield[@id='a'], 10, 4)"/>
        <xsl:variable name="sf_a_pos_13_16" select="substring(subfield[@id='a'], 14, 4)"/>
        <xsl:if test="indicator[@id ='1'][1] = ' ' and indicator[@id ='2'][1]= ' ' and not($sf_a_pos_9_12 = '9999')">
            <xsl:if test="$sf_a_pos_9_12 &gt;= '0'">
                <field name="date_of_publication_t">
                    <xsl:value-of select="$sf_a_pos_9_12"/>
                </field>
            </xsl:if>
            <xsl:if test="$sf_a_pos_13_16 &gt;= '0' and $sf_a_pos_13_16 &lt; '9999' and not($sf_a_pos_13_16 = '    ')">
                <field name="date_of_publication_t">
                    <xsl:value-of select="$sf_a_pos_13_16"/>
                </field>
            </xsl:if>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='210']/subfield[@id='d']">
        <field name="date_of_publication_t">
            <xsl:value-of select="."/>
        </field>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->


<xsl:template name="Extract-facet-date-of-publication">
    <xsl:for-each select="field[@id='100']">
        <xsl:variable name="sf_a_pos_9_12" select="substring(subfield[@id='a'], 10, 4)"/>
        <xsl:variable name="sf_a_pos_13_16" select="substring(subfield[@id='a'], 14, 4)"/>
        <xsl:if test="indicator[@id ='1'][1] = ' ' and indicator[@id ='2'][1]= ' ' and not($sf_a_pos_9_12 = '9999')">
            <xsl:if test="$sf_a_pos_9_12 &gt;= '0'">
                <field name="date_of_publication_s">
                    <xsl:value-of select="$sf_a_pos_9_12"/>
                </field>
            </xsl:if>
            <xsl:if test="$sf_a_pos_13_16 &gt;= '0' and $sf_a_pos_13_16 &lt; '9999' and not($sf_a_pos_13_16 = '    ')">
                <field name="date_of_publication_s">
                    <xsl:value-of select="$sf_a_pos_13_16"/>
                </field>
            </xsl:if>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='210']/subfield[@id='d']">
        <field name="date_of_publication_s">
            <xsl:value-of select="."/>
        </field>
    </xsl:for-each>
</xsl:template>



<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Code-language">
    <!--
        101-#$a
    -->
    <xsl:for-each select="field[@id='101']/subfield[@id='a']">
        <xsl:if test="../indicator[@id='2'] = ' '">
            <field name="code_language_s">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
</xsl:template>


<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<!--
    102##$a
    102##$b
    210##$a
    620##$a
    620##$b
    620##$c
    620##$d
-->
<xsl:template name="Place-publication">
    <xsl:for-each select="field[@id='102']/subfield[@id='a']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='102']/subfield[@id='b']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='210']/subfield[@id='a']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='620']/subfield[@id='a']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='620']/subfield[@id='b']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='620']/subfield[@id='c']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='620']/subfield[@id='d']">
        <xsl:if test="../indicator[@id='1'] = ' ' and ../indicator[@id='2'] = ' '">
            <field name="place_publication_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Title">
    <field name="title_t">
        <xsl:choose>
            <!--
            Если аналитический уровень, то не индексируем 46* поля
            -->
            <xsl:when test="leader/leader07 ='a'">
                <xsl:for-each
                        select="field[(@id &gt; '399' and @id &lt; '460') or (@id &gt; '469' and @id &lt; '500')]/subfield[@id=1]">
                    <xsl:call-template name="Title"/>
                </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <xsl:for-each select="field[@id &gt; '399' and @id &lt; '500']/subfield[@id=1]">
                    <xsl:call-template name="Title-former"/>
                </xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text> </xsl:text>
        <xsl:call-template name="Title-former"/>
    </field>
</xsl:template>

<xsl:template name="Title-former">
    <xsl:for-each select="field[@id='200']">
        <!--
        2001#$a{. $h, $i}
        2001#$i
        -->
        <xsl:if test="(subfield[@id='a'] or subfield[@id='i'])">
            <xsl:value-of select="subfield[@id='a']"/>
            <xsl:for-each select="subfield">
                <xsl:choose>
                    <xsl:when test="@id='e'">
                        <xsl:text>: </xsl:text>
                        <xsl:value-of select="."/>
                    </xsl:when>
                    <xsl:when test="@id='h'">
                        <xsl:text>. </xsl:text>
                        <xsl:value-of select="."/>
                    </xsl:when>
                    <xsl:when test="@id='i'">
                        <xsl:text>, </xsl:text>
                        <xsl:value-of select="."/>
                    </xsl:when>
                    <!--<xsl:when test="@id='v'">
                        <xsl:text>. </xsl:text>
                        <xsl:value-of select="."/>
                        <xsl:text>. </xsl:text>
                    </xsl:when>-->
                </xsl:choose>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='225']">
        <!--
        2250#$a{. $h, $i}
        2251#$a{. $h, $i}
        2251#$i
        -->
        <xsl:if test="subfield[@id='a'] and indicator[@id='1'][1] = '1' or indicator[@id='0'][1]">
            <!--<field name="title">-->
            <xsl:text> </xsl:text>
            <xsl:value-of select="subfield[@id='a']"/>
            <xsl:for-each select="subfield[@id='h']">
                <xsl:text>. </xsl:text>
                <xsl:value-of select="."/>
                <xsl:if test="@id='i'">
                    <xsl:text>, </xsl:text>
                    <xsl:value-of select="subfield[@id='i']"/>
                </xsl:if>

            </xsl:for-each>
            <!--</field>-->
        </xsl:if>
        <!--
        2252#$i
        -->
        <xsl:if test="indicator[@id='1'][1] = '2'">
            <xsl:for-each select="subfield[@id='i']">
                <!--<field name="title">-->
                <xsl:text> </xsl:text>
                <xsl:value-of select="."/>
                <xsl:text> </xsl:text>
                <!--</field>-->
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
</xsl:template>
<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Analitic-title">
    <xsl:if test="leader/leader07 ='a'">
        <xsl:for-each select="field[@id='461']/subfield[@id='1']">
            <xsl:call-template name="Analitic-title-former"/>
        </xsl:for-each>
    </xsl:if>
</xsl:template>

<xsl:template name="Analitic-title-former">
    <xsl:for-each select="field[@id='200']">
        <!--
        2001#$a{. $h, $i}
        2001#$i
        -->
        <field name="analitic_title_t">
            <xsl:if test="(subfield[@id='a'] or subfield[@id='i'])">
                <xsl:value-of select="subfield[@id='a']"/>
                <xsl:for-each select="subfield">
                    <xsl:choose>
                        <xsl:when test="@id='e'">
                            <xsl:text>: </xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:when>
                        <xsl:when test="@id='h'">
                            <xsl:text>. </xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:when>
                        <xsl:when test="@id='i'">
                            <xsl:text>, </xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:when>
                        <xsl:when test="@id='v'">
                            <xsl:text>. </xsl:text>
                            <xsl:value-of select="."/>
                            <xsl:text>. </xsl:text>
                        </xsl:when>
                    </xsl:choose>
                </xsl:for-each>
                <xsl:if test="not(subfield[@id='v'])">
                    <!--<xsl:text>. </xsl:text>-->
                </xsl:if>
            </xsl:if>
        </field>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="ISBN">
    <!--
        010##$a
        421#-1010##$a
        422#-1010##$a
        45-#-1010##$a
        463#-1010##$a
        470#-1010##$a
        48-#-1010##$a
    -->
    <xsl:for-each select="field[@id='010']">
        <xsl:if test="indicator[@id='1']= ' ' and indicator[@id ='2']= ' '">
            <xsl:for-each select="subfield[@id='a']">
                <field name="isbn_t">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="field[@id='421' or @id='422' or @id='463' or @id='470']/subfield[@id='1']">
        <xsl:if test="../indicator[@id ='1'][1]= ' '">
            <xsl:call-template name="ISBN"/>
        </xsl:if>
    </xsl:for-each>

    <xsl:for-each
            select="field[(@id &gt; '449' and @id &lt; '460') or (@id &gt; '479' and @id &lt; '490')]/subfield[@id='1']">
        <xsl:if test="../indicator[@id ='1'][1]= ' '">
            <xsl:call-template name="ISBN"/>
        </xsl:if>
    </xsl:for-each>
</xsl:template>


<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="ISSN">
    <!--
        011##$a
        225-#$x
        461#-$1011##$a
        462#-$1011##$a
    -->
    <xsl:for-each select="field[@id='011']">
        <xsl:if test="indicator[@id='1']= ' ' and indicator[@id ='2']= ' '">
            <xsl:for-each select="subfield[@id='a']">
                <field name="issn_s">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="field[@id='225']">
        <xsl:if test="indicator[@id ='2']= ' '">
            <xsl:for-each select="subfield[@id='x']">
                <field name="issn_s">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:if>
    </xsl:for-each>

    <xsl:for-each select="field[@id='461' or @id='462']/subfield[@id='1']">
        <xsl:if test="../indicator[@id ='1'][1]= ' '">
            <xsl:call-template name="ISSN"/>
        </xsl:if>
    </xsl:for-each>
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
<xsl:template name="Author">
    <xsl:for-each select="field[@id &gt; '699' and @id &lt; '702']">
        <xsl:variable name="sf_a" select="subfield[@id='a'][1]"/>
        <xsl:choose>
            <!--
                70-#1$a, $g ($c)
                70-#1$a, $b ($c)
            -->
            <xsl:when test="$sf_a and indicator[@id='1']=' ' and indicator[@id='2']='1'">
                <xsl:for-each select="subfield[@id='g'][1]">
                    <field name="author_t">
                        <xsl:value-of select="$sf_a"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="."/>
                        <xsl:if test="subfield[@id='c'][1]">
                            <xsl:text> (</xsl:text>
                            <xsl:value-of select="subfield[@id='c'][1]"/>
                            <xsl:text>) </xsl:text>
                        </xsl:if>
                    </field>
                </xsl:for-each>
                <xsl:for-each select="subfield[@id='b'][1]">
                    <field name="author_t">
                        <xsl:value-of select="$sf_a"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="."/>
                        <xsl:if test="subfield[@id='c'][1]">
                            <xsl:text> (</xsl:text>
                            <xsl:value-of select="subfield[@id='c'][1]"/>
                            <xsl:text>) </xsl:text>
                        </xsl:if>
                    </field>
                </xsl:for-each>
                <xsl:if test="not(subfield[@id='b'][1]) and not(subfield[@id='g'][1])">
                    <field name="author_t">
                        <xsl:value-of select="$sf_a"/>
                    </field>
                </xsl:if>
            </xsl:when>
            <!--
                70-#0$a $d ($c)
            -->
            <xsl:when test="$sf_a and indicator[@id='1']=' ' and indicator[@id='2']='0'">
                <field name="author_t">
                    <xsl:value-of select="$sf_a"/>
                    <xsl:for-each select="subfield[@id='d'][1]">
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="."/>
                        <xsl:if test="subfield[@id='c'][1]">
                            <xsl:text> (</xsl:text>
                            <xsl:value-of select="subfield[@id='c'][1]"/>
                            <xsl:text>) </xsl:text>
                        </xsl:if>
                    </xsl:for-each>
                </field>
            </xsl:when>
        </xsl:choose>
    </xsl:for-each>
    <xsl:for-each select="field[@id &gt; '399' and @id &lt; '500']/subfield[@id=1]">
        <xsl:call-template name="Author"/>
    </xsl:for-each>
</xsl:template>
<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Facet-author">
    <xsl:for-each select="field[@id &gt; '699' and @id &lt; '702']">
        <xsl:variable name="sf_a" select="subfield[@id='a'][1]"/>
        <xsl:choose>
            <!--
                70-#1$a, $g ($c)
                70-#1$a, $b ($c)
            -->
            <xsl:when test="$sf_a and indicator[@id='1']=' ' and indicator[@id='2']='1'">
                <xsl:choose>
                    <xsl:when test="subfield[@id='g'][1] and not(subfield[@id='b'][1])">
                        <xsl:for-each select="subfield[@id='g'][1]">
                            <field name="author_s">
                                <xsl:value-of select="$sf_a"/>
                                <xsl:text> </xsl:text>
                                <xsl:value-of select="."/>
                                <xsl:if test="subfield[@id='c'][1]">
                                    <xsl:text> (</xsl:text>
                                    <xsl:value-of select="subfield[@id='c'][1]"/>
                                    <xsl:text>) </xsl:text>
                                </xsl:if>
                            </field>
                        </xsl:for-each>
                    </xsl:when>
                    <xsl:when test="subfield[@id='b'][1]">
                        <xsl:for-each select="subfield[@id='b'][1]">
                            <field name="author_s">
                                <xsl:value-of select="$sf_a"/>
                                <xsl:text> </xsl:text>
                                <xsl:value-of select="."/>
                                <xsl:if test="subfield[@id='c'][1]">
                                    <xsl:text> (</xsl:text>
                                    <xsl:value-of select="subfield[@id='c'][1]"/>
                                    <xsl:text>) </xsl:text>
                                </xsl:if>
                            </field>
                        </xsl:for-each>
                    </xsl:when>
                    <xsl:otherwise>
                        <field name="author_s">
                            <xsl:value-of select="$sf_a"/>
                        </field>
                    </xsl:otherwise>
                </xsl:choose>

            </xsl:when>
            <!--
                70-#0$a $d ($c)
            -->
            <xsl:when test="$sf_a and indicator[@id='1']=' ' and indicator[@id='2']='0'">
                <field name="author_s">
                    <xsl:value-of select="$sf_a"/>
                    <xsl:for-each select="subfield[@id='d'][1]">
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="."/>
                        <xsl:if test="subfield[@id='c'][1]">
                            <xsl:text> (</xsl:text>
                            <xsl:value-of select="subfield[@id='c'][1]"/>
                            <xsl:text>) </xsl:text>
                        </xsl:if>
                    </xsl:for-each>
                </field>
            </xsl:when>
        </xsl:choose>
    </xsl:for-each>
    <xsl:for-each select="field[@id &gt; '399' and @id &lt; '500']/subfield[@id=1]">
        <xsl:call-template name="Author"/>
    </xsl:for-each>
</xsl:template>
<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Publisher">
    <!--
        210##$с
    -->
    <xsl:for-each select="field[@id='210']/subfield[@id='c']">
        <xsl:if test="../indicator[@id='1'][1] = ' ' and ../indicator[@id='2'][1] = ' '">
            <field name="publisher_t">
                <xsl:value-of select="."/>
            </field>
        </xsl:if>
    </xsl:for-each>
</xsl:template>



<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Bib-level">
    <xsl:for-each select="leader/leader07">
        <field name="bib_level_s">
            <xsl:value-of select="."/>
        </field>
    </xsl:for-each>
</xsl:template>

<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
<xsl:template name="Content-type">
    <xsl:variable name="f105_a" select="field[@id='105']/subfield[@id='a']"/>
    <xsl:variable name="f105_a_pos_4" select="substring($f105_a, 5, 1)"/>
    <xsl:variable name="f105_a_pos_5" select="substring($f105_a, 6, 1)"/>
    <xsl:variable name="f105_a_pos_6" select="substring($f105_a, 7, 1)"/>
    <xsl:variable name="f105_a_pos_7" select="substring($f105_a, 8, 1)"/>
    <xsl:if test="$f105_a_pos_4 and $f105_a_pos_4 !=' ' and $f105_a_pos_4 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="$f105_a_pos_4"/>
        </field>
    </xsl:if>
    <xsl:if test="$f105_a_pos_5 and $f105_a_pos_5 !=' ' and $f105_a_pos_5 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="$f105_a_pos_5"/>
        </field>
    </xsl:if>
    <xsl:if test="$f105_a_pos_6 and $f105_a_pos_6 !=' ' and $f105_a_pos_6 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="$f105_a_pos_6"/>
        </field>
    </xsl:if>
    <xsl:if test="$f105_a_pos_7 and $f105_a_pos_7 !=' ' and $f105_a_pos_7 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="$f105_a_pos_7"/>
        </field>
    </xsl:if>

    <xsl:variable name="f110_a" select="field[@id='110']/subfield[@id='a']"/>
    <xsl:variable name="f110_a_pos_3" select="substring($f110_a, 4, 1)"/>
    <xsl:variable name="f110_a_pos_4" select="substring($f110_a, 5, 1)"/>
    <xsl:variable name="f110_a_pos_5" select="substring($f110_a, 6, 1)"/>
    <xsl:variable name="f110_a_pos_6" select="substring($f110_a, 7, 1)"/>

    <xsl:if test="f110_a_pos_3 and f110_a_pos_3 !=' ' and f110_a_pos_3 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="f110_a_pos_3"/>
        </field>
    </xsl:if>
    <xsl:if test="f110_a_pos_4 and f110_a_pos_4 !=' ' and f110_a_pos_4 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="f110_a_pos_4"/>
        </field>
    </xsl:if>
    <xsl:if test="f110_a_pos_5 and f110_a_pos_5 !=' ' and f110_a_pos_5 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="f110_a_pos_5"/>
        </field>
    </xsl:if>
    <xsl:if test="f110_a_pos_6 and f110_a_pos_6 !=' ' and f110_a_pos_6 !='|'">
        <field name="content_type_s">
            <xsl:value-of select="f110_a_pos_6"/>
        </field>
    </xsl:if>

</xsl:template>
<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

<xsl:template name="Linked-record-number">
    <xsl:for-each select="field[@id='461']/subfield[@id='1']/field[@id='001']">
        <field name="linked_record-number_s">
            <xsl:value-of select="."/>
        </field>
    </xsl:for-each>
</xsl:template>

<xsl:template name="Linked-authority-number">
    <xsl:for-each select="field[@id &gt; '699' and @id &lt; '702']">
        <xsl:for-each select="subfield[@id='3']">
            <field name="linked_authority_number_s">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>

<xsl:template name="Linked-subject-number">
    <xsl:for-each select="field[@id='606']">
        <xsl:for-each select="subfield[@id='3']">
            <field name="linked_subject_number_s">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>

<xsl:template name="All">

        <xsl:for-each select="field[@id='001']">
            <field name="all_tru">
                <xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
            </field>
        </xsl:for-each>

        <xsl:for-each select="field[@id &gt;= '200' and @id &lt;= '399']">
            <field name="all_tru">
                <xsl:for-each select="subfield">
                    <xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
                </xsl:for-each>
            </field>
        </xsl:for-each>


        <xsl:for-each select="field[@id &gt;= '500' and @id &lt;= '899']">
            <field name="all_tru">
                <xsl:for-each select="subfield">
                    <xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
                </xsl:for-each>
            </field>
        </xsl:for-each>

    <xsl:for-each select="field[@id &gt;= '400' and @id &lt;= '499']">
        <xsl:for-each select="subfield">
            <xsl:call-template name="All"/>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>

</xsl:stylesheet>



