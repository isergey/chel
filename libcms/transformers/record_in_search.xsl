<?xml version="1.0" encoding="UTF-8"?>
<!--
 Представление записи при выводе в результате поиска
 Структура результирующего документа должна быть следующей:
<doc>
    <field name='field_name_1'>
        <item>Содержимое поля 1 </item>
        <item>Содержимое поля 2 </item>
    </field>
    <field name='field_name_2'>
        <item>Содержимое поля 1 </item>
        <item>Содержимое поля 2 </item>
    </field>
</doc>

Для того, чтобы можно было искать по полю, необходимо задавать ему имя соответвующей точке доступа
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
        <xsl:if test="record">
            <xsl:variable name="leader7" select="leader/leader07"/>

            <xsl:apply-templates select="record"/>
        </xsl:if>
    </xsl:template>

    <!-- match on marcxml record -->
    <xsl:template match="record">
        <doc>
            <xsl:call-template name="Local-number"/>
            <xsl:call-template name="Title"/>
            <xsl:call-template name="Author"/>
            <xsl:call-template name="Subject-heading"/>
            <!--<xsl:call-template name="Subject-subheading"/>-->
            <xsl:call-template name="Subject-keywords"/>
            <xsl:call-template name="Date-of-publication"/>
            <xsl:call-template name="Code-language"/>
            <xsl:call-template name="Publisher"/>
            <xsl:call-template name="Content-type"/>
            <xsl:call-template name="Bib-level"/>
            <xsl:call-template name="Holders"/>
            <xsl:call-template name="Fond"/>
            <xsl:call-template name="Cover"/>
            <xsl:call-template name="Linked-record-number"/>
            <xsl:call-template name="Catalog"/>
            <xsl:call-template name="URL"/>
            <xsl:call-template name="date_of_publication_of_original"/>
        </doc>
    </xsl:template>
    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Local-number">
        <xsl:for-each select="field[@id='001']">
            <field name="local_number">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Title">
        <field name="title">
            <xsl:choose>
                <!--
                Если аналитический уровень, то не индексируем 46* поля
                -->
                <xsl:when test="leader/leader07 ='a'">
                    <xsl:for-each
                            select="field[(@id &gt; '460' and @id &lt; '464') or (@id &gt; '469' and @id &lt; '500')]/subfield[@id=1]">
                        <xsl:call-template name="Title"/>
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:for-each select="field[@id &gt; '460' and @id &lt; '500']/subfield[@id=1]">
                        <xsl:call-template name="Title-former">
                            <xsl:with-param name="inner">inner</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:text></xsl:text>
            <xsl:call-template name="Title-former"/>
        </field>
    </xsl:template>
    <xsl:template name="Title-former">
        <xsl:param name="inner"/>
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
                            <xsl:text>:</xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:when>
                        <xsl:when test="@id='h'">
                            <xsl:text>.</xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:when>
                        <xsl:when test="@id='i'">
                            <xsl:text>,</xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:when>
                        <!--<xsl:when test="@id='v'">
                            <xsl:text>. </xsl:text>
                            <xsl:value-of select="."/>
                            <xsl:text>. </xsl:text>
                        </xsl:when>-->
                    </xsl:choose>
                </xsl:for-each>
                <xsl:if test="not(subfield[@id='v'])">
                    <xsl:text>.</xsl:text>
                </xsl:if>


            </xsl:if>
        </xsl:for-each>
        <xsl:if test="$inner!='inner'">
            <xsl:for-each select="field[@id='225']">
                <!--
                2250#$a{. $h, $i}
                2251#$a{. $h, $i}
                2251#$i
                -->
                <xsl:if test="subfield[@id='a'] and indicator[@id='1'][1] = '1' or indicator[@id='0'][1]">
                    <!--<field name="title">-->
                    <xsl:value-of select="subfield[@id='a']"/>
                    <xsl:for-each select="subfield[@id='h']">
                        <xsl:text>.</xsl:text>
                        <xsl:value-of select="."/>
                        <xsl:if test="@id='i'">
                            <xsl:text>,</xsl:text>
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
                        <xsl:value-of select="."/>
                        <xsl:text></xsl:text>
                        <!--</field>-->
                    </xsl:for-each>
                </xsl:if>
            </xsl:for-each>
        </xsl:if>
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
                    <xsl:choose>
                        <xsl:when test="subfield[@id='g'][1] and not(subfield[@id='b'][1])">
                            <xsl:for-each select="subfield[@id='g'][1]">
                                <field name="author">
                                    <xsl:value-of select="$sf_a"/>
                                    <xsl:text></xsl:text>
                                    <xsl:value-of select="."/>
                                    <xsl:if test="subfield[@id='c'][1]">
                                        <xsl:text>(</xsl:text>
                                        <xsl:value-of select="subfield[@id='c'][1]"/>
                                        <xsl:text>)</xsl:text>
                                    </xsl:if>
                                </field>
                            </xsl:for-each>
                        </xsl:when>
                        <xsl:when test="subfield[@id='b'][1]">
                            <xsl:for-each select="subfield[@id='b'][1]">
                                <field name="author">
                                    <xsl:value-of select="$sf_a"/>
                                    <xsl:text></xsl:text>
                                    <xsl:value-of select="."/>
                                    <xsl:if test="subfield[@id='c'][1]">
                                        <xsl:text>(</xsl:text>
                                        <xsl:value-of select="subfield[@id='c'][1]"/>
                                        <xsl:text>)</xsl:text>
                                    </xsl:if>
                                </field>
                            </xsl:for-each>
                        </xsl:when>
                        <xsl:otherwise>
                            <field name="author">
                                <xsl:value-of select="$sf_a"/>
                            </field>
                        </xsl:otherwise>
                    </xsl:choose>

                </xsl:when>
                <!--
                    70-#0$a $d ($c)
                -->
                <xsl:when test="$sf_a and indicator[@id='1']=' ' and indicator[@id='2']='0'">
                    <field name="author">
                        <xsl:for-each select="subfield[@id='d'][1]">
                            <xsl:value-of select="$sf_a"/>
                            <xsl:text></xsl:text>
                            <xsl:value-of select="."/>
                            <xsl:if test="subfield[@id='c'][1]">
                                <xsl:text>(</xsl:text>
                                <xsl:value-of select="subfield[@id='c'][1]"/>
                                <xsl:text>)</xsl:text>
                            </xsl:if>
                        </xsl:for-each>
                    </field>
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
        <!--<xsl:for-each select="field[@id &gt; '399' and @id &lt; '500']/subfield[@id=1]">
            <xsl:call-template name="Author"/>
        </xsl:for-each>-->
    </xsl:template>


    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Subject-heading">
        <xsl:for-each select="field[@id='606']">
            <xsl:if test="indicator[@id ='2'][1]= ' '">
                <xsl:for-each select="subfield[@id='a']">
                    <field name="subject_heading">
                        <xsl:value-of select="."/>
                        <xsl:if test="../subfield[@id='x']">
                            —
                            <xsl:value-of select="../subfield[@id='x']"/>
                        </xsl:if>
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
                    <field name="subject_subheading">
                        <xsl:value-of select="."/>
                    </field>
                </xsl:for-each>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Subject-keywords">
        <xsl:for-each select="field[@id='610']">
            <xsl:for-each select="subfield[@id='a']">
                <field name="subject_keywords">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Date-of-publication">
        <xsl:for-each select="field[@id='210']">
            <xsl:for-each select="subfield[@id='h']">
                <field name="date_of_publication">
                    <xsl:value-of select="."/>
                </field>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Code-language">
        <!--
            101-#$a
        -->
        <xsl:for-each select="field[@id='101']/subfield[@id='a']">
            <xsl:if test="../indicator[@id='2'] = ' '">
                <field name="code_language">
                    <xsl:value-of select="."/>
                </field>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Publisher">
        <!--
            210##$с
        -->
        <xsl:for-each select="field[@id='210']/subfield[@id='c']">
            <xsl:if test="../indicator[@id='1'][1] = ' ' and ../indicator[@id='2'][1] = ' '">
                <field name="publisher">
                    <xsl:value-of select="."/>
                </field>
            </xsl:if>
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
            <field name="content_type">
                <xsl:value-of select="$f105_a_pos_4"/>
            </field>
        </xsl:if>
        <xsl:if test="$f105_a_pos_5 and $f105_a_pos_5 !=' ' and $f105_a_pos_5 !='|'">
            <field name="content-type">
                <xsl:value-of select="$f105_a_pos_5"/>
            </field>
        </xsl:if>
        <xsl:if test="$f105_a_pos_6 and $f105_a_pos_6 !=' ' and $f105_a_pos_6 !='|'">
            <field name="content-type">
                <xsl:value-of select="$f105_a_pos_6"/>
            </field>
        </xsl:if>
        <xsl:if test="$f105_a_pos_7 and $f105_a_pos_7 !=' ' and $f105_a_pos_7 !='|'">
            <field name="content-type">
                <xsl:value-of select="$f105_a_pos_7"/>
            </field>
        </xsl:if>

        <xsl:variable name="f110_a" select="field[@id='110']/subfield[@id='a']"/>
        <xsl:variable name="f110_a_pos_3" select="substring($f110_a, 4, 1)"/>
        <xsl:variable name="f110_a_pos_4" select="substring($f110_a, 5, 1)"/>
        <xsl:variable name="f110_a_pos_5" select="substring($f110_a, 6, 1)"/>
        <xsl:variable name="f110_a_pos_6" select="substring($f110_a, 7, 1)"/>

        <xsl:if test="f110_a_pos_3 and f110_a_pos_3 !=' ' and f110_a_pos_3 !='|'">
            <field name="content_type">
                <xsl:value-of select="f110_a_pos_3"/>
            </field>
        </xsl:if>
        <xsl:if test="f110_a_pos_4 and f110_a_pos_4 !=' ' and f110_a_pos_4 !='|'">
            <field name="content_type">
                <xsl:value-of select="f110_a_pos_4"/>
            </field>
        </xsl:if>
        <xsl:if test="f110_a_pos_5 and f110_a_pos_5 !=' ' and f110_a_pos_5 !='|'">
            <field name="content_type">
                <xsl:value-of select="f110_a_pos_5"/>
            </field>
        </xsl:if>
        <xsl:if test="f110_a_pos_6 and f110_a_pos_6 !=' ' and f110_a_pos_6 !='|'">
            <field name="content_type">
                <xsl:value-of select="f110_a_pos_6"/>
            </field>
        </xsl:if>

    </xsl:template>


    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Bib-level">
        <xsl:for-each select="leader/leader07">
            <field name="bib_level">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Holders">
        <xsl:for-each select="field[@id='850']/subfield[@id='a']">
            <field name="holders">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:template>
    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="Fond">
        <xsl:for-each select="field[@id='313']/subfield[@id='a']">
            <xsl:if test="starts-with(., 'Коллекция: ')">
                <field name="fond">
                    <xsl:value-of select="substring(.,12)"/>
                </field>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>
    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

    <xsl:template name="Cover">

        <xsl:for-each select="field[@id='856']">
            <xsl:if test="subfield[@id='x']='Обложка'">
                <field name="cover">
                    <xsl:value-of select="subfield[@id='u']"/>
                </field>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

    <xsl:template name="Linked-record-number">
        <xsl:for-each select="field[@id='461']/subfield[@id='1']/field[@id='001']">
            <field name="linked_record_number">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

    <xsl:template name="Catalog">
        <xsl:for-each select="field[@id='908']/subfield[@id='a' or @id='A']">
            <field name="catalog">
                <xsl:value-of select="."/>
            </field>
        </xsl:for-each>
    </xsl:template>
    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->

    <xsl:template name="URL">
        <xsl:for-each select="field[@id='856']">
            <xsl:if test="subfield[@id='u']">
                <field name="url">
                    <xsl:value-of select="subfield[@id='u']"/>
                </field>
            </xsl:if>
            <xsl:if test="subfield[@id='2']">
                <field name="url_title">
                    <xsl:value-of select="subfield[@id='2']"/>
                </field>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
    <xsl:template name="date_of_publication_of_original">
        <!-- Если в записе присутвует 463 поле с вложенным подполе 210_d, то дату создания забираем оттуда-->
        <xsl:choose>
            <xsl:when test="field[@id='455']/subfield[@id='1']/field[@id='210']/subfield[@id='d']">
                <xsl:for-each select="field[@id='455']/subfield[@id='1']/field[@id='210']/subfield[@id='d'][1]">
                    <field name="date_of_publication_of_original">
                        <xsl:value-of select="."/>
                    </field>
                </xsl:for-each>
            </xsl:when>
            <!-- Иначе, извлекаем из основного подполя-->
            <xsl:otherwise>
                <xsl:for-each select="field[@id='210']/subfield[@id='d'][1]">
                    <field name="date_of_publication_of_original">
                        <xsl:value-of select="."/>
                    </field>
                </xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>



